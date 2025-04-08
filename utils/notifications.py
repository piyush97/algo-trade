import os
import platform
import subprocess
from datetime import datetime
from typing import Dict, List
import json

class NotificationSystem:
    def __init__(self, enable_sound=True, enable_desktop=True, enable_console=True):
        self.enable_sound = enable_sound
        self.enable_desktop = enable_desktop
        self.enable_console = enable_console
        self.alert_history = []
        
    def send_alert(self, signal_data: Dict):
        """Send trading alert through multiple channels"""
        symbol = signal_data.get('symbol', 'Unknown')
        overall_signal = signal_data.get('overall_signal', 'HOLD')
        confidence = signal_data.get('confidence', 0)
        timestamp = signal_data.get('timestamp', datetime.now())
        
        # Format alert message
        title = f"Trading Alert: {symbol}"
        message = self._format_alert_message(signal_data)
        
        # Send through different channels
        if self.enable_console:
            self._console_alert(signal_data)
        
        if self.enable_desktop:
            self._desktop_notification(title, message)
        
        if self.enable_sound:
            self._sound_alert(overall_signal)
        
        # Store in history
        self.alert_history.append({
            'timestamp': timestamp,
            'symbol': symbol,
            'signal': overall_signal,
            'confidence': confidence,
            'message': message
        })
        
        # Keep only last 100 alerts
        if len(self.alert_history) > 100:
            self.alert_history = self.alert_history[-100:]
    
    def _format_alert_message(self, signal_data: Dict) -> str:
        """Format the alert message"""
        symbol = signal_data.get('symbol', 'Unknown')
        overall_signal = signal_data.get('overall_signal', 'HOLD')
        confidence = signal_data.get('confidence', 0)
        individual_signals = signal_data.get('individual_signals', [])
        
        # Get current price from individual signals
        current_price = 0
        if individual_signals:
            current_price = individual_signals[0].get('current_price', 0)
        
        message = f"{symbol}: {overall_signal} (Confidence: {confidence}%)"
        if current_price > 0:
            message += f"\\nPrice: ${current_price:.2f}"
        
        # Add strategy breakdown
        if individual_signals:
            message += "\\n\\nStrategy Signals:"
            for signal in individual_signals:
                strategy = signal.get('strategy', 'Unknown')
                signal_type = signal.get('signal', 'HOLD')
                strength = signal.get('strength', 0)
                message += f"\\n• {strategy}: {signal_type} ({strength:.1f}%)"
        
        return message
    
    def _console_alert(self, signal_data: Dict):
        """Print alert to console with colors"""
        symbol = signal_data.get('symbol', 'Unknown')
        overall_signal = signal_data.get('overall_signal', 'HOLD')
        confidence = signal_data.get('confidence', 0)
        timestamp = signal_data.get('timestamp', datetime.now())
        individual_signals = signal_data.get('individual_signals', [])
        
        # Color codes
        colors = {
            'STRONG_BUY': '\\033[92m',  # Green
            'BUY': '\\033[92m',
            'WEAK_BUY': '\\033[93m',   # Yellow
            'HOLD': '\\033[94m',       # Blue
            'WEAK_SELL': '\\033[93m',
            'SELL': '\\033[91m',       # Red
            'STRONG_SELL': '\\033[91m',
            'RESET': '\\033[0m'
        }
        
        color = colors.get(overall_signal, colors['RESET'])
        
        print("\\n" + "="*60)
        print(f"{color}🚨 TRADING ALERT: {symbol}{colors['RESET']}")
        print(f"⏰ Time: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{color}📊 Signal: {overall_signal} (Confidence: {confidence}%){colors['RESET']}")
        
        if individual_signals:
            current_price = individual_signals[0].get('current_price', 0)
            if current_price > 0:
                print(f"💰 Current Price: ${current_price:.2f}")
        
        print("\\n📈 Strategy Breakdown:")
        for signal in individual_signals:
            strategy = signal.get('strategy', 'Unknown')
            signal_type = signal.get('signal', 'HOLD')
            strength = signal.get('strength', 0)
            reason = signal.get('reason', 'No reason provided')
            
            signal_color = colors.get(signal_type.split('_')[0], colors['RESET'])
            print(f"  {signal_color}• {strategy}: {signal_type} ({strength:.1f}%){colors['RESET']}")
            print(f"    Reason: {reason}")
        
        print("="*60)
    
    def _desktop_notification(self, title: str, message: str):
        """Send desktop notification"""
        try:
            system = platform.system()
            
            if system == "Darwin":  # macOS
                # Use osascript for macOS notifications
                script = f'''
                display notification "{message}" with title "{title}" sound name "default"
                '''
                subprocess.run(["osascript", "-e", script], check=False)
                
            elif system == "Linux":
                # Use notify-send for Linux
                subprocess.run(["notify-send", title, message], check=False)
                
            elif system == "Windows":
                # Use PowerShell for Windows
                script = f'''
                Add-Type -AssemblyName System.Windows.Forms
                $notification = New-Object System.Windows.Forms.NotifyIcon
                $notification.Icon = [System.Drawing.SystemIcons]::Information
                $notification.BalloonTipTitle = "{title}"
                $notification.BalloonTipText = "{message}"
                $notification.Visible = $true
                $notification.ShowBalloonTip(5000)
                '''
                subprocess.run(["powershell", "-Command", script], check=False)
                
        except Exception as e:
            print(f"❌ Desktop notification failed: {e}")
    
    def _sound_alert(self, signal_type: str):
        """Play sound alert"""
        try:
            system = platform.system()
            
            if system == "Darwin":  # macOS
                if signal_type in ['STRONG_BUY', 'BUY']:
                    # High pitch sound for buy
                    subprocess.run(["afplay", "/System/Library/Sounds/Glass.aiff"], check=False)
                elif signal_type in ['STRONG_SELL', 'SELL']:
                    # Low pitch sound for sell
                    subprocess.run(["afplay", "/System/Library/Sounds/Sosumi.aiff"], check=False)
                else:
                    # Neutral sound
                    subprocess.run(["afplay", "/System/Library/Sounds/Ping.aiff"], check=False)
                    
            elif system == "Linux":
                # Use beep command or speaker-test
                if signal_type in ['STRONG_BUY', 'BUY']:
                    subprocess.run(["beep", "-f", "1000", "-l", "200"], check=False)
                elif signal_type in ['STRONG_SELL', 'SELL']:
                    subprocess.run(["beep", "-f", "400", "-l", "200"], check=False)
                else:
                    subprocess.run(["beep", "-f", "700", "-l", "100"], check=False)
                    
            elif system == "Windows":
                # Use winsound
                import winsound
                if signal_type in ['STRONG_BUY', 'BUY']:
                    winsound.Beep(1000, 200)
                elif signal_type in ['STRONG_SELL', 'SELL']:
                    winsound.Beep(400, 200)
                else:
                    winsound.Beep(700, 100)
                    
        except Exception as e:
            print(f"❌ Sound alert failed: {e}")
    
    def get_alert_history(self, limit: int = 10) -> List[Dict]:
        """Get recent alert history"""
        return self.alert_history[-limit:]
    
    def clear_alert_history(self):
        """Clear alert history"""
        self.alert_history.clear()
        print("🗑️ Alert history cleared")
    
    def save_alerts_to_file(self, filename: str = None):
        """Save alert history to JSON file"""
        if filename is None:
            filename = f"alert_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            # Convert datetime objects to strings for JSON serialization
            history_json = []
            for alert in self.alert_history:
                alert_copy = alert.copy()
                if isinstance(alert_copy['timestamp'], datetime):
                    alert_copy['timestamp'] = alert_copy['timestamp'].isoformat()
                history_json.append(alert_copy)
            
            with open(filename, 'w') as f:
                json.dump(history_json, f, indent=2)
            
            print(f"💾 Alert history saved to {filename}")
            return filename
            
        except Exception as e:
            print(f"❌ Failed to save alert history: {e}")
            return None
    
    def test_notifications(self):
        """Test all notification methods"""
        test_signal = {
            'symbol': 'TEST',
            'overall_signal': 'BUY',
            'confidence': 85.0,
            'timestamp': datetime.now(),
            'individual_signals': [
                {
                    'strategy': 'SMA',
                    'signal': 'BUY',
                    'strength': 75.0,
                    'current_price': 150.25,
                    'reason': 'Test signal generation'
                }
            ]
        }
        
        print("🧪 Testing notification system...")
        self.send_alert(test_signal)
        print("✅ Test notification sent")