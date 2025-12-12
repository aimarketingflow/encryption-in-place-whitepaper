# Technical Diagram Prompts for EiP Whitepaper

6 informative visuals that explain the technology. Each teaches a concept.

---

## 1. EMF Entropy Collection — How It Works
**Section:** 3.2 EMF Entropy Sources  
**What it teaches:** The actual RF spectrum being captured and mixed into entropy

**Prompt:**
```
Technical infographic diagram showing electromagnetic spectrum capture for cryptographic entropy. Left side: labeled RF sources (WiFi 2.4GHz, WiFi 5GHz, Bluetooth 2.4GHz, Cellular 700MHz-2.5GHz, Zigbee 915MHz) shown as distinct frequency bands on a spectrum analyzer display. Center: SDR receiver capturing signals. Right side: entropy mixing process showing SHA-256 hash combining EMF samples + system CSPRNG + timestamp + NFC UID into final entropy pool. Clean technical diagram style, dark background (#0a0e1a), cyan and white labels, no decorative elements, educational infographic
```

**Key info shown:**
- Specific frequency bands being captured
- SDR hardware in the pipeline
- Entropy mixing formula (EMF + CSPRNG + timestamp + NFC UID → SHA-256)

---

## 2. Encryption in Place vs Traditional — Side by Side
**Section:** 4.1 Why "In Place" Matters  
**What it teaches:** The forensic vulnerability of copy-delete vs EiP

**Prompt:**
```
Split technical comparison diagram. LEFT SIDE labeled "Traditional Encryption": shows disk sectors 1000-1003 containing plaintext, arrow to NEW sectors 2000-2003 containing ciphertext, then deletion of original sectors with red warning "Recoverable via forensics". RIGHT SIDE labeled "Encryption in Place (EiP)": shows SAME sectors 1000-1003 transforming from plaintext to ciphertext in place, green checkmark "No forensic artifacts". Include sector numbers, before/after states clearly labeled. Technical blueprint style, dark background, red for vulnerabilities, green for secure, white/cyan labels
```

**Key info shown:**
- Sector-level view of what happens on disk
- Why traditional leaves forensic artifacts
- Why EiP overwrites in place = no recovery

---

## 3. Two-Factor Hardware Authentication Flow
**Section:** 2.1 Definition  
**What it teaches:** The authentication sequence requiring both NFC + USB

**Prompt:**
```
Technical flowchart diagram showing authentication sequence: Step 1: NFC tag tap (shows 7-byte UID extracted), Step 2: USB vault insertion (shows USB fingerprint: vendor ID, product ID, serial), Step 3: Both factors combined and verified against stored binding, Step 4: Master key decrypted only if both match. Include decision diamond "Both factors valid?" with Yes→Unlock and No→Deny paths. Clean flowchart style, dark background, cyan arrows, white text labels, technical diagram not decorative
```

**Key info shown:**
- What data comes from NFC (UID)
- What data comes from USB (fingerprint)
- That BOTH are required — not either/or
- Failure path if factors don't match

---

## 4. Key Derivation Architecture
**Section:** 3. Cryptographic Primitives  
**What it teaches:** How the master key is derived and used

**Prompt:**
```
Technical architecture diagram showing key derivation flow: Top: Entropy Pool (EMF + CSPRNG + NFC + timestamp) feeds into PBKDF2-HMAC-SHA256 box labeled "250,000 iterations" with 256-bit salt input. Output: Master Key. Master Key then feeds into HKDF box which outputs multiple Per-File Keys (Key 1, Key 2, Key 3...) each combined with unique nonce. Final output to AES-256-GCM encryption. Show iteration count prominently. Technical cryptographic diagram style, dark background, labeled boxes and arrows, no decorative elements
```

**Key info shown:**
- PBKDF2 with exact iteration count (250,000)
- Master key derived ONCE
- Per-file keys via HKDF (fast, no PBKDF2 per file)
- Why it's fast: single expensive derivation

---

## 5. File Visibility Removal — Before/After
**Section:** 4.3 File Visibility Removal  
**What it teaches:** What "hidden from OS" actually means technically

**Prompt:**
```
Technical before/after diagram showing file system state. BEFORE: Directory listing showing "Documents/taxes.pdf" with metadata (filename, size, timestamps, location pointer to sector 1000). AFTER EiP: Same directory entry shows scrambled filename "x7k2m9.enc", zeroed timestamps, but sector 1000 still contains encrypted data. Separate panel shows terminal commands "ls", "find", "mdfind" all returning empty results. Include note: "Registry on USB maps original name → encrypted location". Technical file system diagram style, dark background, monospace font for filenames, cyan highlights
```

**Key info shown:**
- Filename scrambling (not just encryption)
- Metadata clearing
- Why OS tools can't find files
- USB registry holds the mapping

---

## 6. Attack Surface Comparison
**Section:** 5.1 Threat Model  
**What it teaches:** What attack vectors are blocked and why

**Prompt:**
```
Technical comparison matrix diagram. Rows: Remote Attack, Device Theft, Forensic Recovery, Ransomware, Brute Force. Columns: Traditional Encryption, Cloud Encryption, EiP. Each cell shows vulnerability status with brief reason. Traditional: Remote=Vulnerable (password online), Theft=Vulnerable (key on device), Forensic=Vulnerable (deleted originals), Ransomware=Vulnerable (files visible). Cloud: Remote=Vulnerable (provider breach), Theft=N/A, Forensic=N/A, Ransomware=Partial. EiP: All cells show "Blocked" with reasons (airgapped keys, separate USB, in-place overwrite, hidden files, 250k PBKDF2). Matrix/table style infographic, dark background, red for vulnerable, green for blocked, technical labels
```

**Key info shown:**
- Specific attack vectors
- WHY each is blocked (not just that it is)
- Direct comparison to alternatives

---

## Style Notes

- **No decorative fluff** — every element teaches something
- **Include actual numbers** — 250,000 iterations, 256-bit, specific frequencies
- **Show the "why"** — not just what, but why it's secure
- **Technical diagram style** — like you'd see in a security whitepaper or RFC
- **Dark background** (#0a0e1a) with cyan (#06b6d4) and white labels

---

## Suggested Placement

| # | Diagram | After Section |
|---|---------|---------------|
| 1 | EMF Entropy Collection | 3.2 EMF Entropy Sources |
| 2 | EiP vs Traditional | 4.1 Why "In Place" Matters |
| 3 | Two-Factor Auth Flow | 2.1 Definition |
| 4 | Key Derivation | 3.1 Key Derivation (or new section) |
| 5 | File Visibility | 4.3 File Visibility Removal |
| 6 | Attack Surface Matrix | 5.1 Threat Model |
