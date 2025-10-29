# 🔧 Manual OTP Fill Guide

Jika Auto-Fill button tidak berfungsi, gunakan cara manual ini:

## Method 1: Copy-Paste dari Console

Buka Chrome Console (F12) di halaman dengan form OTP, lalu paste:

```javascript
// Fill OTP 065873 ke 6 input fields
const otp = '065873';
const inputs = document.querySelectorAll('input:not([type="hidden"])');
const visibleInputs = Array.from(inputs).filter(input => {
  const rect = input.getBoundingClientRect();
  return rect.width > 0 && rect.height > 0;
});

if (visibleInputs.length === 6) {
  visibleInputs.forEach((input, i) => {
    input.value = otp[i];
    input.dispatchEvent(new Event('input', {bubbles: true}));
    input.dispatchEvent(new Event('change', {bubbles: true}));
  });
  console.log('✅ OTP filled!');
} else {
  console.log(`Found ${visibleInputs.length} inputs, need exactly 6`);
}
```

## Method 2: Keyboard Shortcut

1. Pastikan extension sudah ter-install
2. Di halaman dengan form OTP, tekan: **Ctrl+Shift+O**
3. OTP akan auto-fill jika extension mendeteksi field

## Method 3: Direct Message

Buka Console dan jalankan:

```javascript
// Send message langsung ke extension
chrome.runtime.sendMessage(
  chrome.runtime.id,
  { action: 'fillOTP', otp: '065873' },
  response => console.log('Response:', response)
);
```

## Method 4: Force Fill Specific Input

Jika ada input tertentu yang perlu diisi:

```javascript
// Click dulu pada input pertama OTP, lalu run:
const activeElement = document.activeElement;
if (activeElement && activeElement.tagName === 'INPUT') {
  const otp = '065873';
  const parent = activeElement.parentElement.parentElement;
  const inputs = parent.querySelectorAll('input');
  
  inputs.forEach((input, i) => {
    if (i < otp.length) {
      input.value = otp[i];
      input.dispatchEvent(new Event('input', {bubbles: true}));
    }
  });
}
```

## Troubleshooting

### Extension tidak detect fields?

1. **Reload extension:**
   - Buka `chrome://extensions/`
   - Find "TempMail OTP Auto-Fill"
   - Click Reload icon

2. **Refresh halaman:**
   - Ctrl+F5 untuk hard refresh
   - Pastikan extension icon muncul di toolbar

3. **Check Console untuk error:**
   - F12 → Console tab
   - Lihat apakah ada error merah

### OTP tidak ter-fill?

Kemungkinan website menggunakan:
- Shadow DOM
- Dynamic loading
- Custom input components

Solusi: Gunakan Method 1 (copy-paste console)

## Update Extension

Jika masih tidak berfungsi, update extension:

1. Tutup Chrome
2. Buka folder `extension/chrome`
3. Pastikan semua file ter-update
4. Buka Chrome dan reload extension

---

**Note:** OTP dari screenshot Anda adalah **065873**
