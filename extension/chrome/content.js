// Content Script - Runs on web pages to auto-fill OTP

if (window.location.protocol === 'http:' || window.location.protocol === 'https:') {
  console.log('🔐 TempMail OTP Auto-Fill active');
}

// Add keyboard shortcut for manual trigger (Ctrl+Shift+O)
document.addEventListener('keydown', (event) => {
  if (event.ctrlKey && event.shiftKey && event.key === 'O') {
    console.log('🎯 Manual OTP fill triggered');
    
    // Request last OTP from background
    chrome.runtime.sendMessage({ action: 'getStatus' }, (response) => {
      if (response && response.lastOTP) {
        autoFillOTP(response.lastOTP);
      } else {
        console.log('❌ No OTP available');
      }
    });
  }
});

// OTP input selectors
const OTP_SELECTORS = [
  // Name attributes
  'input[name*="otp" i]',
  'input[name*="code" i]',
  'input[name*="verification" i]',
  'input[name*="pin" i]',
  'input[name*="token" i]',
  'input[name*="2fa" i]',
  
  // ID attributes
  'input[id*="otp" i]',
  'input[id*="code" i]',
  'input[id*="verification" i]',
  'input[id*="pin" i]',
  
  // Placeholder attributes
  'input[placeholder*="otp" i]',
  'input[placeholder*="code" i]',
  'input[placeholder*="verification" i]',
  'input[placeholder*="kode" i]', // Indonesian
  
  // Type and length based
  'input[type="number"][maxlength="6"]',
  'input[type="text"][maxlength="6"]',
  'input[type="tel"][maxlength="6"]',
  
  // Class based
  'input[class*="otp" i]',
  'input[class*="code" i]',
  'input[class*="verification" i]',
  
  // Aria labels
  'input[aria-label*="otp" i]',
  'input[aria-label*="code" i]',
  'input[aria-label*="verification" i]'
];

// Submit button selectors
const SUBMIT_SELECTORS = [
  'button[type="submit"]',
  'input[type="submit"]',
  'button:contains("Verify")',
  'button:contains("Submit")',
  'button:contains("Confirm")',
  'button:contains("Verifikasi")', // Indonesian
  'button:contains("Kirim")', // Indonesian
  'button:contains("Continue")',
  'button:contains("Next")',
  'button[class*="submit" i]',
  'button[class*="verify" i]'
];

// Listen for messages from background script
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  console.log('📨 Message received:', request);
  
  if (request.action === 'fillOTP') {
    const result = autoFillOTP(request.otp);
    sendResponse({ success: result });
  }
  
  // Return true to indicate async response
  return true;
});

// Main auto-fill function
function autoFillOTP(otp) {
  console.log(`🔑 Attempting to auto-fill OTP: ${otp}`);
  
  // Clean OTP string (remove spaces if any)
  otp = otp.replace(/\s/g, '');
  
  // Try split OTP fields first (most common)
  let filled = trySplitFields(otp);
  
  // If not filled, try standard OTP fields
  if (!filled) {
    filled = tryStandardFields(otp);
  }
  
  // If still not filled, try generic number fields
  if (!filled) {
    filled = tryGenericFields(otp);
  }
  
  // Last resort: try any visible input
  if (!filled) {
    filled = tryAnyVisibleInputs(otp);
  }
  
  if (filled) {
    console.log('✅ OTP auto-filled successfully');
    highlightSubmitButton();
    showSuccessIndicator();
    
    // Optional: Auto-submit after delay (disabled by default)
    // setTimeout(() => tryAutoSubmit(), 1000);
  } else {
    console.log('❌ No OTP field found');
    showManualCopyPrompt(otp);
  }
  
  return filled;
}

// Try standard OTP input fields
function tryStandardFields(otp) {
  for (const selector of OTP_SELECTORS) {
    const inputs = document.querySelectorAll(selector);
    
    for (const input of inputs) {
      if (isValidOTPField(input)) {
        fillInput(input, otp);
        return true;
      }
    }
  }
  
  return false;
}

// Try split OTP fields (6 separate inputs)
function trySplitFields(otp) {
  console.log('🔍 Looking for split OTP fields...');
  
  // Look for groups of 4-8 single-character inputs
  const singleCharInputs = document.querySelectorAll(
    'input[maxlength="1"], input[size="1"], input[type="text"]:not([maxlength]), input[type="number"]:not([maxlength])'
  );
  
  console.log(`Found ${singleCharInputs.length} potential single-char inputs`);
  
  // Also look for inputs in a flex/grid container
  const containers = document.querySelectorAll('div, section, form');
  for (const container of containers) {
    const inputs = container.querySelectorAll('input:not([type="hidden"]):not([type="submit"])');
    
    // Check for exactly 6 inputs (common for OTP)
    if (inputs.length === 6) {
      // Check if they're visible and arranged horizontally
      let allVisible = true;
      let allOnSameLine = true;
      let firstTop = null;
      
      for (const input of inputs) {
        const rect = input.getBoundingClientRect();
        if (rect.width === 0 || rect.height === 0) {
          allVisible = false;
          break;
        }
        if (firstTop === null) {
          firstTop = rect.top;
        } else if (Math.abs(rect.top - firstTop) > 20) {
          allOnSameLine = false;
          break;
        }
      }
      
      if (allVisible && allOnSameLine) {
        console.log('✅ Found 6 inputs in a row - filling as OTP');
        fillSplitInputs(Array.from(inputs), otp);
        return true;
      }
    }
    
    // Also check for 4-8 small inputs
    if (inputs.length >= 4 && inputs.length <= 8) {
      const firstRect = inputs[0]?.getBoundingClientRect();
      const lastRect = inputs[inputs.length - 1]?.getBoundingClientRect();
      
      if (firstRect && lastRect && Math.abs(firstRect.top - lastRect.top) < 10) {
        console.log(`📦 Found ${inputs.length} inputs in a row`);
        
        let allSmall = true;
        for (const input of inputs) {
          const width = input.getBoundingClientRect().width;
          if (width > 100) {
            allSmall = false;
            break;
          }
        }
        
        if (allSmall) {
          console.log('✅ Filling split OTP fields');
          fillSplitInputs(Array.from(inputs), otp);
          return true;
        }
      }
    }
  }
  
  // Try original grouping method
  const groups = groupNearbyInputs(singleCharInputs);
  
  for (const group of groups) {
    if (group.length >= 4 && group.length <= 8) {
      // Check if it's likely an OTP field group
      if (isLikelyOTPGroup(group)) {
        console.log(`✅ Found OTP group with ${group.length} fields`);
        fillSplitInputs(group, otp);
        return true;
      }
    }
  }
  
  return false;
}

// Try generic number fields
function tryGenericFields(otp) {
  // Look for any number input that could be OTP
  const numberInputs = document.querySelectorAll(
    'input[type="number"], input[type="tel"], input[inputmode="numeric"]'
  );
  
  for (const input of numberInputs) {
    if (isLikelyOTPField(input)) {
      fillInput(input, otp);
      return true;
    }
  }
  
  return false;
}

// Last resort - try any visible inputs
function tryAnyVisibleInputs(otp) {
  console.log('🔍 Last resort: checking all visible inputs');
  
  // Get all visible text/number inputs
  const allInputs = document.querySelectorAll('input[type="text"], input[type="number"], input[type="tel"], input:not([type])');
  
  // Find groups of 6 inputs
  const visibleInputs = [];
  for (const input of allInputs) {
    const rect = input.getBoundingClientRect();
    const style = window.getComputedStyle(input);
    
    // Check if visible
    if (rect.width > 0 && rect.height > 0 && 
        style.display !== 'none' && 
        style.visibility !== 'hidden' &&
        input.type !== 'hidden') {
      visibleInputs.push(input);
    }
  }
  
  console.log(`Found ${visibleInputs.length} visible inputs`);
  
  // If exactly 6 visible inputs, assume OTP
  if (visibleInputs.length === 6) {
    console.log('✅ Found exactly 6 visible inputs - assuming OTP');
    fillSplitInputs(visibleInputs, otp);
    return true;
  }
  
  // If single input that looks like it could hold 6 digits
  for (const input of visibleInputs) {
    if (!input.value && (input.maxLength >= 6 || !input.maxLength)) {
      console.log('✅ Filling single input field');
      fillInput(input, otp);
      return true;
    }
  }
  
  return false;
}

// Check if input is valid OTP field
function isValidOTPField(input) {
  // Skip if already filled
  if (input.value && input.value.length > 0) {
    return false;
  }
  
  // Skip if hidden or disabled
  if (input.type === 'hidden' || input.disabled || input.readOnly) {
    return false;
  }
  
  // Skip if not visible
  const rect = input.getBoundingClientRect();
  if (rect.width === 0 || rect.height === 0) {
    return false;
  }
  
  return true;
}

// Check if input is likely OTP field based on context
function isLikelyOTPField(input) {
  if (!isValidOTPField(input)) {
    return false;
  }
  
  // Check maxlength
  const maxLength = parseInt(input.getAttribute('maxlength') || '0');
  if (maxLength >= 4 && maxLength <= 8) {
    return true;
  }
  
  // Check surrounding text for OTP keywords
  const parent = input.closest('div, form, section');
  if (parent) {
    const text = parent.textContent.toLowerCase();
    const keywords = ['otp', 'code', 'verification', 'verify', 'pin', 'token', 'kode'];
    
    for (const keyword of keywords) {
      if (text.includes(keyword)) {
        return true;
      }
    }
  }
  
  return false;
}

// Group nearby inputs
function groupNearbyInputs(inputs) {
  const groups = [];
  const used = new Set();
  
  for (const input of inputs) {
    if (used.has(input)) continue;
    
    const group = [input];
    used.add(input);
    
    // Find siblings
    let nextSibling = input.nextElementSibling;
    while (nextSibling) {
      if (nextSibling.tagName === 'INPUT' && 
          nextSibling.getAttribute('maxlength') === '1') {
        group.push(nextSibling);
        used.add(nextSibling);
        nextSibling = nextSibling.nextElementSibling;
      } else {
        break;
      }
    }
    
    groups.push(group);
  }
  
  return groups;
}

// Check if group is likely OTP
function isLikelyOTPGroup(group) {
  // Check if all inputs have similar attributes
  const first = group[0];
  const type = first.type;
  const className = first.className;
  
  for (const input of group) {
    if (input.type !== type) return false;
  }
  
  return true;
}

// Fill single input
function fillInput(input, value) {
  input.focus();
  input.value = value;
  
  // Trigger events
  input.dispatchEvent(new Event('input', { bubbles: true }));
  input.dispatchEvent(new Event('change', { bubbles: true }));
  input.dispatchEvent(new KeyboardEvent('keyup', { bubbles: true }));
  
  // Visual feedback
  input.style.transition = 'background-color 0.3s';
  input.style.backgroundColor = '#90EE90';
  setTimeout(() => {
    input.style.backgroundColor = '';
  }, 2000);
}

// Fill split inputs
function fillSplitInputs(inputs, otp) {
  console.log(`📝 Filling ${inputs.length} split inputs with OTP: ${otp}`);
  
  for (let i = 0; i < Math.min(inputs.length, otp.length); i++) {
    const input = inputs[i];
    const digit = otp[i];
    
    // Clear first
    input.value = '';
    
    // Set value
    input.value = digit;
    
    // Trigger all possible events
    input.dispatchEvent(new Event('input', { bubbles: true }));
    input.dispatchEvent(new Event('change', { bubbles: true }));
    input.dispatchEvent(new KeyboardEvent('keydown', { key: digit, bubbles: true }));
    input.dispatchEvent(new KeyboardEvent('keyup', { key: digit, bubbles: true }));
    
    // Visual feedback
    input.style.transition = 'all 0.3s';
    input.style.backgroundColor = '#90EE90';
    input.style.transform = 'scale(1.1)';
    
    setTimeout(() => {
      input.style.backgroundColor = '';
      input.style.transform = '';
    }, 2000);
    
    // Move focus to next input with delay
    if (i < inputs.length - 1) {
      setTimeout(() => {
        inputs[i + 1].focus();
      }, 100 * (i + 1));
    }
  }
  
  console.log('✅ Split inputs filled');
}

// Highlight submit button
function highlightSubmitButton() {
  for (const selector of SUBMIT_SELECTORS) {
    const buttons = document.querySelectorAll(selector);
    
    for (const button of buttons) {
      if (isVisible(button)) {
        button.style.transition = 'all 0.3s';
        button.style.transform = 'scale(1.05)';
        button.style.boxShadow = '0 0 20px rgba(33, 150, 243, 0.5)';
        
        setTimeout(() => {
          button.style.transform = '';
          button.style.boxShadow = '';
        }, 2000);
        
        return;
      }
    }
  }
}

// Check if element is visible
function isVisible(element) {
  const rect = element.getBoundingClientRect();
  return rect.width > 0 && rect.height > 0 && 
         rect.top < window.innerHeight && 
         rect.bottom > 0;
}

// Show success indicator
function showSuccessIndicator() {
  const indicator = document.createElement('div');
  indicator.innerHTML = `
    <div style="
      position: fixed;
      top: 20px;
      right: 20px;
      background: #4CAF50;
      color: white;
      padding: 15px 20px;
      border-radius: 5px;
      box-shadow: 0 2px 10px rgba(0,0,0,0.2);
      z-index: 999999;
      font-family: Arial;
      font-size: 14px;
      display: flex;
      align-items: center;
      animation: slideIn 0.3s ease;
    ">
      <span style="margin-right: 10px;">✅</span>
      OTP Auto-Filled Successfully!
    </div>
  `;
  
  // Add animation
  const style = document.createElement('style');
  style.textContent = `
    @keyframes slideIn {
      from { transform: translateX(100%); }
      to { transform: translateX(0); }
    }
  `;
  document.head.appendChild(style);
  
  document.body.appendChild(indicator);
  
  // Remove after 3 seconds
  setTimeout(() => {
    indicator.style.animation = 'slideOut 0.3s ease';
    setTimeout(() => indicator.remove(), 300);
  }, 3000);
}

// Show manual copy prompt
function showManualCopyPrompt(otp) {
  const prompt = document.createElement('div');
  prompt.innerHTML = `
    <div style="
      position: fixed;
      bottom: 20px;
      right: 20px;
      background: #2196F3;
      color: white;
      padding: 15px;
      border-radius: 5px;
      box-shadow: 0 2px 10px rgba(0,0,0,0.2);
      z-index: 999999;
      font-family: Arial;
      font-size: 14px;
      max-width: 300px;
    ">
      <div style="margin-bottom: 10px;">
        📋 OTP Ready to Copy:
      </div>
      <div style="
        background: rgba(255,255,255,0.2);
        padding: 10px;
        border-radius: 3px;
        font-family: monospace;
        font-size: 18px;
        text-align: center;
        cursor: pointer;
      " onclick="navigator.clipboard.writeText('${otp}'); this.textContent='Copied!'">
        ${otp}
      </div>
      <div style="margin-top: 10px; font-size: 12px; opacity: 0.9;">
        Click the code to copy
      </div>
    </div>
  `;
  
  document.body.appendChild(prompt);
  
  // Remove after 10 seconds
  setTimeout(() => prompt.remove(), 10000);
}

// Optional: Auto-submit (disabled by default)
function tryAutoSubmit() {
  // Uncomment to enable auto-submit
  /*
  for (const selector of SUBMIT_SELECTORS) {
    const button = document.querySelector(selector);
    if (button && isVisible(button)) {
      console.log('🚀 Auto-submitting form');
      button.click();
      return;
    }
  }
  */
}

// Monitor for dynamically added OTP fields
const observer = new MutationObserver((mutations) => {
  // Check if new OTP fields were added
  for (const mutation of mutations) {
    if (mutation.type === 'childList') {
      for (const node of mutation.addedNodes) {
        if (node.nodeType === 1) { // Element node
          // Check if it's an OTP field
          const inputs = node.querySelectorAll ? 
                        node.querySelectorAll('input') : [];
          for (const input of inputs) {
            if (isLikelyOTPField(input)) {
              console.log('🔍 New OTP field detected');
            }
          }
        }
      }
    }
  }
});

// Start observing
observer.observe(document.body, {
  childList: true,
  subtree: true
});

// Extension ready
