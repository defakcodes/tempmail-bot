// Background Service Worker for OTP Auto-Fill
// Manages WebSocket connection and message routing

let socket = null;
let userId = null;
let reconnectTimer = null;
let isConnected = false;
let lastOTP = null;
let currentEmail = null;

// Initialize on install
chrome.runtime.onInstalled.addListener(() => {
  console.log('🚀 OTP Auto-Fill Extension installed');
  loadUserConfig();
});

// Load user configuration
async function loadUserConfig() {
  const result = await chrome.storage.sync.get(['userId', 'autoConnect']);
  
  if (result.userId) {
    userId = result.userId;
    if (result.autoConnect !== false) {
      connectWebSocket();
    }
  }
}

// Connect to WebSocket server
function connectWebSocket() {
  if (!userId) {
    console.error('❌ No user ID configured');
    return;
  }
  
  if (socket && socket.readyState === WebSocket.OPEN) {
    console.log('✅ Already connected');
    return;
  }
  
  console.log(`🔌 Connecting to WebSocket as ${userId}...`);
  socket = new WebSocket(`ws://localhost:8000/ws/${userId}`);
  
  socket.onopen = () => {
    console.log('✅ WebSocket connected');
    isConnected = true;
    clearTimeout(reconnectTimer);
    
    // Update badge
    chrome.action.setBadgeText({ text: '✓' });
    chrome.action.setBadgeBackgroundColor({ color: '#4CAF50' });
    
    // Notify popup if open
    chrome.runtime.sendMessage({
      type: 'connection_status',
      connected: true
    }).catch(() => {});
    
    // Send initial status request
    socket.send(JSON.stringify({ type: 'status' }));
  };
  
  socket.onmessage = async (event) => {
    const data = JSON.parse(event.data);
    console.log('📨 Received:', data);
    
    switch(data.type) {
      case 'otp':
        await handleOTP(data);
        break;
        
      case 'new_email':
        currentEmail = data.email;
        await chrome.storage.local.set({ currentEmail: data.email });
        
        // Notify popup
        chrome.runtime.sendMessage({
          type: 'new_email',
          email: data.email
        }).catch(() => {});
        
        // Show notification
        chrome.notifications.create({
          type: 'basic',
          iconUrl: 'icon128.png',
          title: 'New Email Generated',
          message: `Email: ${data.email}`,
          buttons: [{ title: 'Copy' }]
        });
        break;
        
      case 'status':
        currentEmail = data.email;
        break;
        
      case 'ping':
        socket.send(JSON.stringify({ type: 'pong' }));
        break;
    }
  };
  
  socket.onerror = (error) => {
    console.error('❌ WebSocket error:', error);
    isConnected = false;
  };
  
  socket.onclose = () => {
    console.log('🔌 WebSocket disconnected');
    isConnected = false;
    
    // Update badge
    chrome.action.setBadgeText({ text: '!' });
    chrome.action.setBadgeBackgroundColor({ color: '#F44336' });
    
    // Notify popup
    chrome.runtime.sendMessage({
      type: 'connection_status',
      connected: false
    }).catch(() => {});
    
    // Auto reconnect after 5 seconds
    clearTimeout(reconnectTimer);
    reconnectTimer = setTimeout(() => {
      console.log('🔄 Attempting to reconnect...');
      connectWebSocket();
    }, 5000);
  };
}

// Handle incoming OTP
async function handleOTP(data) {
  lastOTP = data.otp;
  
  // Store OTP
  await chrome.storage.local.set({
    lastOTP: data.otp,
    lastOTPTime: Date.now(),
    lastOTPEmail: data.email,
    lastOTPSender: data.sender
  });
  
  // Show notification
  chrome.notifications.create('otp-received', {
    type: 'basic',
    iconUrl: 'icon128.png',
    title: '🔑 OTP Received!',
    message: `OTP: ${data.otp}\nFrom: ${data.sender}`,
    buttons: [
      { title: 'Auto-Fill' },
      { title: 'Copy' }
    ],
    requireInteraction: true
  });
  
  // Update badge
  chrome.action.setBadgeText({ text: data.otp.substring(0, 3) });
  chrome.action.setBadgeBackgroundColor({ color: '#2196F3' });
  
  // Auto-fill in active tab
  const [activeTab] = await chrome.tabs.query({ active: true, currentWindow: true });
  if (activeTab) {
    await autoFillOTP(activeTab.id, data.otp);
  }
}

// Auto-fill OTP in tab
async function autoFillOTP(tabId, otp) {
  try {
    await chrome.tabs.sendMessage(tabId, {
      action: 'fillOTP',
      otp: otp
    });
    
    console.log(`✅ OTP sent to tab ${tabId}`);
  } catch (error) {
    console.error('❌ Failed to send OTP to tab:', error);
  }
}

// Handle notification buttons
chrome.notifications.onButtonClicked.addListener(async (notifId, btnIdx) => {
  if (notifId === 'otp-received') {
    if (btnIdx === 0) {
      // Auto-Fill button
      const [activeTab] = await chrome.tabs.query({ active: true, currentWindow: true });
      if (activeTab && lastOTP) {
        await autoFillOTP(activeTab.id, lastOTP);
      }
    } else if (btnIdx === 1) {
      // Copy button
      await copyToClipboard(lastOTP);
    }
  }
});

// Copy to clipboard helper
async function copyToClipboard(text) {
  try {
    await chrome.tabs.create({
      url: 'data:text/html,<html><body><textarea id="t">' + 
           text + '</textarea><script>document.getElementById("t").select();' +
           'document.execCommand("copy");window.close();</script></body></html>',
      active: false
    });
  } catch (error) {
    console.error('Failed to copy:', error);
  }
}

// Listen for messages from popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  switch(request.action) {
    case 'connect':
      if (request.userId) {
        userId = request.userId;
        chrome.storage.sync.set({ userId: userId });
        connectWebSocket();
      }
      break;
      
    case 'disconnect':
      if (socket) {
        socket.close();
        socket = null;
      }
      clearTimeout(reconnectTimer);
      break;
      
    case 'getStatus':
      sendResponse({
        connected: isConnected,
        userId: userId,
        lastOTP: lastOTP,
        currentEmail: currentEmail
      });
      break;
      
    case 'manualFill':
      if (request.otp) {
        chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
          if (tabs[0]) {
            autoFillOTP(tabs[0].id, request.otp);
          }
        });
      }
      break;
  }
  
  return true;
});

// Keep service worker alive
setInterval(() => {
  if (socket && socket.readyState === WebSocket.OPEN) {
    socket.send(JSON.stringify({ type: 'ping' }));
  }
}, 25000);

// Initialize
loadUserConfig();
