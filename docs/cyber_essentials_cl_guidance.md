---
tags: [company-docs]
---

# Cyber Essentials BYOD Guidance for Cottage Labs

Related: [[Ops_handbook]], [[remote_worker_hardware_inventory]]

This document provides guidance for developers using their own devices (BYOD) to meet UK Cyber Essentials certification requirements for Cottage Labs.

## Operating System and Application Requirements

### Supported Systems
- **Operating System**: Must be fully supported by the manufacturer and receive regular security updates
  - Windows: Windows 11 with current support lifecycle
  - macOS: Currently supported versions receiving security updates
  - Linux: Supported distributions with active security update channels
- **Applications**: Only use software that is actively maintained and receives security patches
- **End-of-Life Software**: Remove any applications or operating systems that are no longer supported

### Security Updates
- **Requirement**: Install security updates within 14 days of release
- **Automatic Updates**: Enable automatic security updates where possible
- **Manual Updates**: For systems requiring manual updates, check weekly and apply promptly
- **Documentation**: Keep a record of major system updates applied

## Network Security

### Home Router and Network Equipment (Recommended)
Home routers not supplied by Cottage Labs are outside the scope of our Cyber Essentials certification - the software firewall on your device (below) is the required control. The following is still strongly recommended good practice:
- **Default Passwords**: Change all default administrator passwords on routers, switches, and network equipment
- **Strong Authentication**: Use strong, unique passwords (minimum 12 characters) for all network device admin accounts
- **Firmware Updates**: Keep router and network equipment firmware updated to latest stable versions
- **Remote Management**: Disable remote management features unless absolutely necessary
- **Internet-Facing Management**: Router management interfaces and firewall configuration should not be accessible from the internet - management should only be possible from the local network
- **WPS**: Disable WPS (Wi-Fi Protected Setup) on wireless routers
- **Guest Networks**: Use separate guest networks for visitors, isolated from business network

### Software Firewalls (Required)
- **Windows**: Windows Defender Firewall must be enabled and properly configured
- **macOS**: Built-in firewall must be activated
- **Linux**: ufw is installed but **disabled by default** on Ubuntu - enable it with `sudo ufw enable` and confirm that `sudo ufw status` shows `Status: active` (or use an equivalent, active iptables/nftables ruleset)
- **Configuration**: Default deny incoming connections; outbound traffic may be allowed
- **Third-party Firewalls**: If using third-party solutions, ensure they are kept updated

## User Account Management

### Administrator Privileges
- **Separate Admin Account (Required)**: Every computer used for Cottage Labs work must have a separate local administrator account, and the account you use day to day must be a standard (non-administrator) user - even if you are the only person who uses the computer
- **Everyday Use**: Do web browsing, email and office work only from your standard account; never use the administrator account for these
- **Elevation Only When Needed**: Carry out administrative tasks (installing software, changing system settings) by entering the administrator account's credentials at the operating system's elevation prompt - UAC on Windows, administrator authentication on macOS, `su`/`sudo` as the admin account on Linux
- **Keep Prompts Enabled**: Do not disable UAC, and do not configure passwordless (`NOPASSWD`) sudo
- **Admin Password**: The administrator account needs its own strong, unique password (at least 12 characters), stored in your password manager

#### Setting Up Account Separation
- **Windows**: Settings > Accounts > Other users > Add account - create a local administrator account (e.g. `admin`) and set its account type to Administrator. Sign in to it once, then change your everyday account's type to Standard User
- **macOS**: System Settings > Users & Groups > Add User - create an Administrator account. Then select your everyday account and turn off "Allow this user to administer this computer"
- **Ubuntu**: create an admin user with `sudo adduser admin && sudo usermod -aG sudo admin`, confirm `su - admin -c 'sudo -v'` works, then remove your everyday user from the `sudo` (and `docker`) groups with `sudo deluser $USER sudo`. For admin tasks, run `su - admin` first. Use rootless Docker for everyday development

### Multi-Factor Authentication (Required)
- **All Work Accounts**: MFA must be enabled on every cloud service account used for Cottage Labs work
- **Google Sign-in**: Where a service offers "Sign in with Google", use your Cottage Labs Google account, which is protected by MFA
- **Services Without MFA**: If a service you need does not offer MFA, tell the systems administration team before using it

### Password Requirements

#### Creating Strong Passwords
- **Length Over Complexity**: Use minimum 12 characters, preferably longer
- **Three Random Words**: Follow NCSC guidance - use three unrelated words (e.g., "coffee-tiger-mountain")
- **Avoid Common Patterns**: Do not use pet names, keyboard patterns (qwerty123), or passwords used elsewhere
- **Uniqueness**: Every work account must have a unique password
- **No Regular Expiry**: Passwords do not need to be changed regularly unless compromised

#### Password Manager Usage
- **Recommended Tool**: Use a reputable password manager to generate and store unique passwords
- **Master Password**: The master password must be exceptional quality - long, unique, and memorable only to you
- **Secure Storage**: Choose a password manager with strong encryption and regular security audits
- **Built-in Generators**: Use the password manager's generator feature for creating complex passwords
- **Two-Factor Authentication**: Enable 2FA on your password manager account where available

## Device Security

### Automatic Locking
- **Screen Lock**: Configure automatic screen lock after 5-10 minutes of inactivity
- **Lock Requirements**: a PIN of at least 6 digits (used only to unlock the device, e.g. Windows Hello or phone PIN), or a password of at least 12 characters
- **Biometric Authentication**: Use fingerprint, face recognition, or similar where available
- **Sleep/Hibernate**: Configure system to require authentication after sleep/hibernate

### Malware Protection
Every device must be protected by anti-malware software, or by application allow listing (only approved, signed applications from approved sources), as appropriate to its operating system:
- **Windows**: Microsoft Defender Antivirus must be enabled with real-time protection and automatic definition updates, and Microsoft Defender SmartScreen enabled to block malicious websites
- **macOS**: Keep the built-in XProtect and Gatekeeper protections enabled and automatic security updates turned on
- **Linux**: Protected by application allow listing - only install applications from the approved list and approved sources (see Application Management). Anti-malware software such as ClamAV is optional
- **Browsers**: Keep Safe Browsing (Chrome/Chromium) or Deceptive Content and Dangerous Software Protection (Firefox) enabled
- **Mobile Devices**: Only install apps from official app stores (Google Play, Apple App Store)

## Application Management

### Approved Software Sources and Code Signing

**Mandatory Requirement**: Only signed software from approved sources may be installed on devices accessing company resources.

#### Approved App Stores and Sources
- **Mobile Devices (iOS/Android)**: Applications must be installed exclusively from:
  - Apple App Store (iOS devices)
  - Google Play Store (Android devices)
- **Desktop/Laptop Computers**: Software must be obtained from:
  - Official vendor websites with verified digital signatures
  - Microsoft Store (Windows)
  - Mac App Store (macOS)
  - Official distribution repositories (Linux: apt, yum, dnf, etc.)
  - The Snap Store (Linux)
  - Signed vendor package repositories added following the vendor's official instructions (e.g. Google Chrome, Visual Studio Code, Docker)
- **Browser Extensions**: Only from official browser extension stores (Chrome Web Store, Firefox Add-ons, etc.)
- **Development Dependencies**: Libraries and packages installed for project work from official package registries (e.g. PyPI, npm) are permitted

#### Code Signing Verification
- **Digital Signatures**: All installed software must have valid digital signatures from trusted publishers
- **Unsigned Software**: Installation of unsigned or self-signed software is prohibited unless explicitly approved by the systems administration team
- **Verification Process**: Check publisher certificates before installation on desktop systems
- **Warning Prompts**: Do not bypass operating system warnings about unsigned or untrusted software
- **Linux Specifics**: Do not install manually downloaded `.deb` packages, AppImages, or `curl | bash` style install scripts unless approved by the systems administration team

### Approved Applications
Only applications on this list (plus software supplied as part of a supported operating system) may be installed on devices used for Cottage Labs work. The list is maintained by the systems administration team - ask them to add anything you need.

- **Browsers**: Mozilla Firefox, Google Chrome, Chromium, Microsoft Edge, Safari
- **Email**: Gmail (web), Mozilla Thunderbird, Apple Mail
- **Office**: Google Workspace (web), Microsoft Office, LibreOffice, WPS Office
- **Development**: Visual Studio Code, Git, Docker, language runtimes and their package managers (e.g. Python, Node.js), terminal emulators and SSH clients
- **Communication**: Zoom, Slack, Discord, Mattermost
- **Security**: Passbolt, Google Authenticator (or another reputable authenticator app)

*Approved applications list last reviewed: 2026-10-14*

#### Prohibited Sources
- **Third-party App Stores**: No sideloading or alternative app stores (e.g., APK files from websites)
- **Pirated Software**: Use of unlicensed or pirated software is strictly forbidden
- **Unverified Downloads**: Software from file-sharing sites, torrents, or unofficial mirrors
- **Modified Software**: Repackaged or modified versions of official applications

### Software Installation
- **Business Need**: Only install applications necessary for work purposes
- **Regular Review**: Monthly review of installed applications
- **Installation Approval**: When in doubt about a software source, consult with the systems administration team before installation

### Application Maintenance
- **Unused Software**: Uninstall applications that are no longer needed
- **Update Management**: Keep all applications updated to latest stable versions
- **Inventory**: Maintain awareness of what software is installed on your device

## Security Incidents

### Lost or Stolen Devices
- **Immediate Reporting**: Report lost or stolen devices to management immediately
- **Contact Information**: Emergency contact details are available in the employee handbook
- **Timeline**: Report within 2 hours during business hours, or first thing the next business day
- **Information Required**: Device description, last known location, potential data exposure

### Prohibited Activities
- **Rooting/Jailbreaking**: Strictly prohibited on any device used for business purposes
- **Unauthorized Modifications**: Do not bypass built-in security features
- **Security Software**: Do not disable or circumvent security applications

## Monitoring and Compliance

### Compliance Demonstration
- **Screen-share Tours**: Compliance may be verified through screen-share demonstrations on reasonable request
- **Cooperation**: Employees must cooperate with security audits and compliance checks
- **Privacy**: Personal data will be respected during any compliance demonstration

### Business Context
- **Remote Access**: Cottage Labs disables direct remote access to production services
- **Data Handling**: Development work uses anonymized data sets
- **Risk Assessment**: These measures reflect our lower risk profile while maintaining certification compliance

## Implementation Checklist

- [ ] Operating system is current and supported
- [ ] Automatic security updates enabled
- [ ] Router/network equipment default passwords changed (recommended)
- [ ] Router firmware updated to latest version (recommended)
- [ ] Software firewall activated and configured (Linux: `sudo ufw status` shows `active`)
- [ ] Separate administrator account created; everyday account is a standard user
- [ ] Elevation prompts (UAC / sudo password) left enabled
- [ ] MFA enabled on all work accounts
- [ ] Strong passwords/PINs implemented
- [ ] Automatic screen lock configured (≤10 minutes)
- [ ] Windows/macOS: built-in anti-malware enabled and updating
- [ ] Only approved applications from approved sources installed
- [ ] Unnecessary applications removed
- [ ] Emergency contact information saved
- [ ] Device security features (biometrics) enabled where available

## Support and Questions

For questions about this guidance or assistance with implementation, contact the systems administration team. Regular compliance reviews will be conducted to ensure ongoing adherence to these requirements.

---

*This document supports Cottage Labs' UK Cyber Essentials certification requirements. Last updated: 2026-10-29*