# Cyber Essentials BYOD Guidance for Cottage Labs

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

### Router and Network Equipment Security
- **Default Passwords**: Change all default administrator passwords on routers, switches, and network equipment
- **Strong Authentication**: Use strong, unique passwords (minimum 12 characters) for all network device admin accounts
- **Firmware Updates**: Keep router and network equipment firmware updated to latest stable versions
- **Remote Management**: Disable remote management features unless absolutely necessary
- **Internet-Facing Management**: Router management interfaces and firewall configuration must NOT be accessible from the internet - management should only be possible from the local network
- **WPS**: Disable WPS (Wi-Fi Protected Setup) on wireless routers
- **Guest Networks**: Use separate guest networks for visitors, isolated from business network

### Software Firewalls
- **Windows**: Windows Defender Firewall must be enabled and properly configured
- **macOS**: Built-in firewall must be activated
- **Linux**: Configure and enable ufw, iptables, or equivalent firewall solution
- **Configuration**: Default deny incoming connections, allow only necessary outbound traffic
- **Third-party Firewalls**: If using third-party solutions, ensure they are kept updated

## User Account Management

### Separate User and Administrator Accounts
- **Daily Use Account**: Use a standard user account for day-to-day work
- **Administrator Account**: Maintain a separate administrator account for system changes
- **Privilege Escalation**: Use sudo/Run as Administrator only when necessary
- **Account Naming**: Use descriptive names that distinguish between user and admin accounts

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
- **Lock Requirements**: 6-digit minimum PIN or strong password
- **Biometric Authentication**: Use fingerprint, face recognition, or similar where available
- **Sleep/Hibernate**: Configure system to require authentication after sleep/hibernate

### Anti-malware Protection
- **Installation Required**: Install reputable anti-malware software on all devices
- **Real-time Protection**: Enable real-time scanning and protection
- **Regular Updates**: Ensure malware definitions are updated automatically
- **Regular Scans**: Perform full system scans weekly
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
- **Browser Extensions**: Only from official browser extension stores (Chrome Web Store, Firefox Add-ons, etc.)

#### Code Signing Verification
- **Digital Signatures**: All installed software must have valid digital signatures from trusted publishers
- **Unsigned Software**: Installation of unsigned or self-signed software is prohibited unless explicitly approved by the systems administration team
- **Verification Process**: Check publisher certificates before installation on desktop systems
- **Warning Prompts**: Do not bypass operating system warnings about unsigned or untrusted software

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
- [ ] Router/network equipment default passwords changed
- [ ] Router firmware updated to latest version
- [ ] Software firewall activated and configured
- [ ] Separate user and administrator accounts created
- [ ] Strong passwords/PINs implemented
- [ ] Automatic screen lock configured (≤10 minutes)
- [ ] Anti-malware software installed and updated
- [ ] Unnecessary applications removed
- [ ] Emergency contact information saved
- [ ] Device security features (biometrics) enabled where available

## Support and Questions

For questions about this guidance or assistance with implementation, contact the systems administration team. Regular compliance reviews will be conducted to ensure ongoing adherence to these requirements.

---

*This document supports Cottage Labs' UK Cyber Essentials certification requirements. Last updated: 2025-10-09*