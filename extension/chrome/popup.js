// Popup script for extension UI

let isConnected = false;
let currentUserId = null;
let lastOTP = null;

// DOM Elements
const elements = {
  statusDot: document.getElementById('statusDot'),
  statusText: document.getElementById('statusText'),
  userIdInput: document.getElementById('userIdInput'),
  connectBtn: document.getElementById('connectBtn'),
  disconnectBtn: document.getElementById('disconnectBtn'),
  setupSection: document.getElementById('setupSection'),
  infoSection: document.getElementById('infoSection'),
  otpSection: document.getElementById('otpSection'),
  emptyState: document.getElementById('emptyState'),
  currentUserId: document.getElementById('currentUserId'),
  currentEmail: document.getElementById('currentEmail'),
  otpDisplay: document.getElementById('otpDisplay'),
  otpCode: document.getElementById('otpCode'),
  otpTime: document.getElementById('otpTime'),
  autoFillBtn: document.getElementById('autoFillBtn'),
  copyBtn: document.getElementById('copyBtn'),
  notification: document.getElementById('notification')
};

// Initialize
document.addEventListener('DOMContentLoaded', async () => {
  await loadStatus();
  setupEventListeners();
});

// Load current status
async function loadStatus() {
  // Get saved user ID
  const result = await chrome.storage.sync.get(['userId']);
  if (result.userId) {
    currentUserId = result.userId;
    elements.userIdInput.value = currentUserId;
  }
  
  // Get connection status from background
  chrome.runtime.sendMessage({ action: 'getStatus' }, (response) => {
    if (response) {
      updateConnectionStatus(response.connected);
      
      if (response.connected) {
        currentUserId = response.userId;
        showConnectedState();
        
        if (response.currentEmail) {
          elements.currentEmail.textContent = response.currentEmail;
        }
      }
      
      if (response.lastOTP) {
        showOTP(response.lastOTP);
      }
    }
  });
  
  // Load last OTP from storage
  const otpData = await chrome.storage.local.get(['lastOTP', 'lastOTPTime']);
  if (otpData.lastOTP) {
    showOTP(otpData.lastOTP, otpData.lastOTPTime);
  }
}

// Setup event listeners
function setupEventListeners() {
  // Connect button
  elements.connectBtn.addEventListener('click', async () => {
    const userId = elements.userIdInput.value.trim();
    
    if (!userId) {
      showNotification('Please enter a User ID', 'error');
      return;
    }
    
    // Save user ID
    await chrome.storage.sync.set({ userId: userId });
    currentUserId = userId;
    
    // Connect via background
    chrome.runtime.sendMessage({ 
      action: 'connect', 
      userId: userId 
    });
    
    showNotification('Connecting...', 'info');
  });
  
  // Disconnect button
  elements.disconnectBtn.addEventListener('click', () => {
    chrome.runtime.sendMessage({ action: 'disconnect' });
    showDisconnectedState();
    showNotification('Disconnected', 'info');
  });
  
  // Auto-fill button
  elements.autoFillBtn.addEventListener('click', async () => {
    if (lastOTP) {
      // Get active tab
      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
      
      if (tab) {
        // Send directly to content script
        try {
          await chrome.tabs.sendMessage(tab.id, {
            action: 'fillOTP',
            otp: lastOTP
          });
          showNotification('Auto-filling OTP...', 'success');
          
          // Close popup after short delay
          setTimeout(() => window.close(), 500);
        } catch (error) {
          console.error('Failed to send to tab:', error);
          // Fallback to background
          chrome.runtime.sendMessage({ 
            action: 'manualFill', 
            otp: lastOTP 
          });
          showNotification('Trying auto-fill...', 'info');
        }
      }
    }
  });
  
  // Copy button
  elements.copyBtn.addEventListener('click', async () => {
    if (lastOTP) {
      await navigator.clipboard.writeText(lastOTP);
      showNotification('OTP copied!', 'success');
      
      // Change button text temporarily
      elements.copyBtn.innerHTML = '<span>✅</span> Copied!';
      setTimeout(() => {
        elements.copyBtn.innerHTML = '<span>📋</span> Copy';
      }, 2000);
    }
  });
  
  // Dashboard link
  document.getElementById('dashboardLink').addEventListener('click', (e) => {
    e.preventDefault();
    chrome.tabs.create({ url: 'http://103.158.13.181:8000/dashboard' });
  });
  
  // Help link
  document.getElementById('helpLink').addEventListener('click', (e) => {
    e.preventDefault();
    showHelp();
  });
  
  // Enter key on input
  elements.userIdInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
      elements.connectBtn.click();
    }
  });
}

// Update connection status
function updateConnectionStatus(connected) {
  isConnected = connected;
  
  if (connected) {
    elements.statusDot.classList.remove('disconnected');
    elements.statusDot.classList.add('connected');
    elements.statusText.textContent = 'CONNECTED';
  } else {
    elements.statusDot.classList.remove('connected');
    elements.statusDot.classList.add('disconnected');
    elements.statusText.textContent = 'DISCONNECTED';
  }
}

// Show connected state
function showConnectedState() {
  elements.setupSection.style.display = 'none';
  elements.infoSection.style.display = 'block';
  elements.currentUserId.textContent = currentUserId;
  
  if (!lastOTP) {
    elements.emptyState.style.display = 'block';
    elements.otpSection.style.display = 'none';
  } else {
    elements.emptyState.style.display = 'none';
    elements.otpSection.style.display = 'block';
  }
}

// Show disconnected state
function showDisconnectedState() {
  updateConnectionStatus(false);
  elements.setupSection.style.display = 'block';
  elements.infoSection.style.display = 'none';
  elements.otpSection.style.display = 'none';
  elements.emptyState.style.display = 'none';
}

// Show OTP
function showOTP(otp, timestamp) {
  lastOTP = otp;
  
  elements.otpCode.textContent = otp;
  
  if (timestamp) {
    const date = new Date(timestamp);
    const timeStr = date.toLocaleTimeString();
    elements.otpTime.textContent = `Received at ${timeStr}`;
  } else {
    elements.otpTime.textContent = 'Just received';
  }
  
  elements.otpDisplay.style.display = 'block';
  elements.emptyState.style.display = 'none';
  elements.otpSection.style.display = 'block';
}

// Show notification
function showNotification(message, type = 'info') {
  const colors = {
    info: '#2196F3',
    success: '#4CAF50',
    error: '#f44336',
    warning: '#FF9800'
  };
  
  elements.notification.style.background = colors[type] || colors.info;
  elements.notification.textContent = message;
  elements.notification.style.display = 'block';
  
  setTimeout(() => {
    elements.notification.style.display = 'none';
  }, 3000);
}

// Show help
function showHelp() {
  alert(`
How to use TempMail OTP Auto-Fill:

1. Get your User ID from the Telegram bot
2. Enter the User ID and click Connect
3. Generate an email in the Telegram bot
4. When OTP is received, it will auto-fill
5. Or click Auto-Fill button manually

Troubleshooting:
- Make sure the server is running
- Check your User ID is correct
- Refresh the page if OTP doesn't fill
  `);
}

// Listen for messages from background
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  switch(message.type) {
    case 'connection_status':
      updateConnectionStatus(message.connected);
      if (message.connected) {
        showConnectedState();
        showNotification('Connected successfully!', 'success');
      } else {
        showNotification('Connection lost', 'error');
      }
      break;
      
    case 'new_email':
      elements.currentEmail.textContent = message.email;
      showNotification(`New email: ${message.email}`, 'info');
      break;
      
    case 'otp_received':
      showOTP(message.otp, Date.now());
      showNotification(`OTP received: ${message.otp}`, 'success');
      break;
  }
});

// Auto-refresh status every 2 seconds
setInterval(() => {
  chrome.runtime.sendMessage({ action: 'getStatus' }, (response) => {
    if (response) {
      updateConnectionStatus(response.connected);
    }
  });
}, 2000);
