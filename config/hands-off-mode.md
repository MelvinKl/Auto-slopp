# Auto-slopp Hands-off Mode

This configuration makes the Auto-slopp system run completely hands-off without any user interactions.

## Environment Variables

### Core Settings
- `AUTO_CONFIRM=true` - Automatically confirms all prompts
- `INTERACTIVE_MODE=false` - Disables interactive mode
- `AUTO_INSTALL_PACKAGES=true` - Auto-installs missing packages

### Service Management
- `FORCE_INSTALL=true` - Forces service installation without confirmation
- `FORCE_ROOT=true` - Allows running as root without warnings

### Branch Management
- `CONFIRM_BEFORE_DELETE=false` - Skips branch deletion confirmations
- `CONFIRMATION_TIMEOUT=0` - No timeout for confirmations

### Security
- `SKIP_TOKEN_CONFIRMATION=true` - Skips token confirmation prompts

## Usage

### Enable Hands-off Mode
```bash
source config/hands-off-mode.sh
```

### Run Scripts Hands-off
```bash
# Enable hands-off mode
source config/hands-off-mode.sh

# Run any script - no prompts will appear
./scripts/deploy-setup.sh
./scripts/install-service.sh
./scripts/cleanup-branches-enhanced.sh
```

### Temporary Override
```bash
# Enable hands-off mode but keep one interaction
AUTO_CONFIRM=false ./scripts/deploy-setup.sh
```

## Safety Considerations

This mode is designed for automated environments where:
- The system is trusted to make correct decisions
- All configurations are pre-set
- Logging provides sufficient audit trails
- Rollback procedures are in place

For development or manual operations, keep these variables unset or set to `false`.