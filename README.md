# Sports Odds Data Collection Tool

A Python-based data collection tool that gathers publicly available sports betting odds and market data from various sources. This project is designed for **educational and research purposes only**.

## ⚠️ Important Legal Notice

**This tool is for educational and research purposes only. Users are responsible for:**
- Complying with all applicable terms of service
- Respecting rate limits and robots.txt files
- Using data responsibly and ethically
- Understanding local laws regarding data collection

**The authors are not affiliated with any sportsbook or betting platform.**

## 🔒 Security Notice

**All API URLs and endpoints have been removed from this repository for safety and legal compliance.**
- Users must provide their own API endpoints
- No hardcoded URLs to external services are included
- This prevents potential terms of service violations
- Users are responsible for finding and using appropriate data sources

## Features

- Collects publicly available sports betting odds data
- Supports multiple sports (MLB, NBA, NFL, NHL)
- Extracts various market types (spreads, totals, moneylines, player props)
- Outputs data in structured formats (JSON/CSV)
- Modular design for easy extension

## Supported Sports & Markets

- **MLB**: Game lines, player props, team totals, inning props
- **NBA**: Game lines, (Can be extended to more markets)
- **NFL**: Game lines, (Can be extended to more markets)
- **NHL**: Game lines, (Can be extended to more markets)

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Important Setup Notes
**Before using this tool, you must:**
1. **Add your own API endpoints** - All URLs have been removed for safety
2. **Configure your data sources** - Replace placeholder URLs with your own
3. **Ensure legal compliance** - Verify you have permission to access your data sources

### Basic Example
```python
# Example structure (URLs removed for safety)
urls = [
    # ("Game", "YOUR_API_ENDPOINT_HERE"),
    # ("Player_Props", "YOUR_API_ENDPOINT_HERE"),
    # Add your own endpoints here
]
```

### Data Collection
```bash
# Run MLB data collection (after configuring endpoints)
python MLB/Run_all_scripts.py

# Run specific sport collection
python NBA/NBA.py
```

## Project Structure

```
├── MLB/                 # Major League Baseball data collection
├── NBA/                 # National Basketball Association data collection  
├── NFL/                 # National Football League data collection
├── NHL/                 # National Hockey League data collection
├── dk-odds-scraper/     # DraftKings client library
```

## Data Output

All collected data is saved in structured JSON format with the following organization:
- Game lines and spreads
- Player prop bets
- Team totals and over/under markets
- Inning-specific and game-specific props

## Legal Compliance

This tool:
- Uses only publicly available endpoints
- Implements reasonable rate limiting
- Includes proper user-agent headers
- Respects robots.txt guidelines
- Does not require authentication for public data

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This software is provided "as is" without warranty of any kind. The authors are not responsible for any misuse of this tool or violation of terms of service. Users assume all responsibility for compliance with applicable laws and terms of service.
