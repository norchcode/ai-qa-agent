"""
Android Device module for AI QA Agent.
This module provides functionality for managing Android devices for testing.
"""
import os
import logging
import subprocess
import time
import re
from typing import Dict, List, Any, Optional, Tuple

logger = logging.getLogger(__name__)

class AndroidDevice:
    """Class for managing Android devices for testing."""
    
    def __init__(self, device_id: Optional[str] = None):
        """
        Initialize the Android Device.
        
        Args:
            device_id: Optional device ID. If not provided, will use the first available device.
        """
        self.device_id = device_id
        self.device_info = {}
        self.connected = False
        
        # Initialize device
        self._initialize_device()
        
        logger.info(f"Initialized Android Device: {self.device_id}")
    
    def _initialize_device(self) -> None:
        """Initialize the Android device."""
        # If no device ID provided, get the first available device
        if not self.device_id:
            devices = self.get_connected_devices()
            if devices:
                self.device_id = devices[0]
                logger.info(f"Using first available device: {self.device_id}")
            else:
                logger.warning("No Android devices connected")
                return
        
        # Check if the device is connected
        self.connected = self._check_device_connected()
        
        if self.connected:
            # Get device information
            self.device_info = self._get_device_info()
        else:
            logger.warning(f"Device {self.device_id} is not connected")
    
    def _check_device_connected(self) -> bool:
        """
        Check if the device is connected.
        
        Returns:
            True if the device is connected, False otherwise.
        """
        try:
            result = subprocess.run(
                ['adb', 'devices'], 
                capture_output=True, 
                text=True, 
                check=True
            )
            
            # Parse the output to check if the device is connected
            lines = result.stdout.strip().split('\n')
            for line in lines[1:]:  # Skip the first line (header)
                if line.strip():
                    parts = line.split()
                    if parts[0] == self.device_id and parts[1] == 'device':
                        return True
            
            return False
        except subprocess.CalledProcessError as e:
            logger.error(f"Error checking device connection: {e}")
            return False
    
    def _get_device_info(self) -> Dict[str, str]:
        """
        Get information about the device.
        
        Returns:
            Dictionary containing device information.
        """
        info = {}
        
        try:
            # Get device model
            result = subprocess.run(
                ['adb', '-s', self.device_id, 'shell', 'getprop', 'ro.product.model'],
                capture_output=True,
                text=True,
                check=True
            )
            info['model'] = result.stdout.strip()
            
            # Get Android version
            result = subprocess.run(
                ['adb', '-s', self.device_id, 'shell', 'getprop', 'ro.build.version.release'],
                capture_output=True,
                text=True,
                check=True
            )
            info['android_version'] = result.stdout.strip()
            
            # Get screen resolution
            result = subprocess.run(
                ['adb', '-s', self.device_id, 'shell', 'wm', 'size'],
                capture_output=True,
                text=True,
                check=True
            )
            match = re.search(r'Physical size: (\d+x\d+)', result.stdout)
            if match:
                info['screen_resolution'] = match.group(1)
            
            # Get device serial number
            info['serial'] = self.device_id
            
            return info
        except subprocess.CalledProcessError as e:
            logger.error(f"Error getting device info: {e}")
            return {}
    
    @staticmethod
    def get_connected_devices() -> List[str]:
        """
        Get a list of connected Android devices.
        
        Returns:
            List of device IDs.
        """
        try:
            result = subprocess.run(
                ['adb', 'devices'], 
                capture_output=True, 
                text=True, 
                check=True
            )
            
            # Parse the output to get device IDs
            devices = []
            lines = result.stdout.strip().split('\n')
            for line in lines[1:]:  # Skip the first line (header)
                if line.strip():
                    parts = line.split()
                    if parts[1] == 'device':
                        devices.append(parts[0])
            
            return devices
        except subprocess.CalledProcessError as e:
            logger.error(f"Error getting connected devices: {e}")
            return []
    
    def is_connected(self) -> bool:
        """
        Check if the device is connected.
        
        Returns:
            True if the device is connected, False otherwise.
        """
        return self._check_device_connected()
    
    def get_info(self) -> Dict[str, str]:
        """
        Get information about the device.
        
        Returns:
            Dictionary containing device information.
        """
        if not self.connected:
            logger.warning(f"Device {self.device_id} is not connected")
            return {}
        
        return self.device_info
    
    def install_app(self, apk_path: str) -> bool:
        """
        Install an app on the device.
        
        Args:
            apk_path: Path to the APK file.
            
        Returns:
            True if the installation was successful, False otherwise.
        """
        if not self.connected:
            logger.warning(f"Device {self.device_id} is not connected")
            return False
        
        logger.info(f"Installing app from {apk_path} on device {self.device_id}")
        
        try:
            subprocess.run(
                ['adb', '-s', self.device_id, 'install', '-r', apk_path],
                check=True
            )
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Error installing app: {e}")
            return False
    
    def uninstall_app(self, package_name: str) -> bool:
        """
        Uninstall an app from the device.
        
        Args:
            package_name: Package name of the app to uninstall.
            
        Returns:
            True if the uninstallation was successful, False otherwise.
        """
        if not self.connected:
            logger.warning(f"Device {self.device_id} is not connected")
            return False
        
        logger.info(f"Uninstalling app {package_name} from device {self.device_id}")
        
        try:
            subprocess.run(
                ['adb', '-s', self.device_id, 'uninstall', package_name],
                check=True
            )
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Error uninstalling app: {e}")
            return False
    
    def start_app(self, package_name: str, activity_name: Optional[str] = None) -> bool:
        """
        Start an app on the device.
        
        Args:
            package_name: Package name of the app to start.
            activity_name: Optional activity name to start. If not provided, will start the main activity.
            
        Returns:
            True if the app was started successfully, False otherwise.
        """
        if not self.connected:
            logger.warning(f"Device {self.device_id} is not connected")
            return False
        
        logger.info(f"Starting app {package_name} on device {self.device_id}")
        
        try:
            if activity_name:
                # Start specific activity
                subprocess.run(
                    ['adb', '-s', self.device_id, 'shell', 'am', 'start', '-n', f"{package_name}/{activity_name}"],
                    check=True
                )
            else:
                # Start main activity
                subprocess.run(
                    ['adb', '-s', self.device_id, 'shell', 'monkey', '-p', package_name, '-c', 'android.intent.category.LAUNCHER', '1'],
                    check=True
                )
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Error starting app: {e}")
            return False
    
    def stop_app(self, package_name: str) -> bool:
        """
        Stop an app on the device.
        
        Args:
            package_name: Package name of the app to stop.
            
        Returns:
            True if the app was stopped successfully, False otherwise.
        """
        if not self.connected:
            logger.warning(f"Device {self.device_id} is not connected")
            return False
        
        logger.info(f"Stopping app {package_name} on device {self.device_id}")
        
        try:
            subprocess.run(
                ['adb', '-s', self.device_id, 'shell', 'am', 'force-stop', package_name],
                check=True
            )
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Error stopping app: {e}")
            return False
    
    def clear_app_data(self, package_name: str) -> bool:
        """
        Clear app data on the device.
        
        Args:
            package_name: Package name of the app to clear data for.
            
        Returns:
            True if the app data was cleared successfully, False otherwise.
        """
        if not self.connected:
            logger.warning(f"Device {self.device_id} is not connected")
            return False
        
        logger.info(f"Clearing app data for {package_name} on device {self.device_id}")
        
        try:
            subprocess.run(
                ['adb', '-s', self.device_id, 'shell', 'pm', 'clear', package_name],
                check=True
            )
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Error clearing app data: {e}")
            return False
    
    def take_screenshot(self, output_path: str) -> bool:
        """
        Take a screenshot of the device.
        
        Args:
            output_path: Path to save the screenshot to.
            
        Returns:
            True if the screenshot was taken successfully, False otherwise.
        """
        if not self.connected:
            logger.warning(f"Device {self.device_id} is not connected")
            return False
        
        logger.info(f"Taking screenshot on device {self.device_id}")
        
        try:
            # Take screenshot on device
            device_path = '/sdcard/screenshot.png'
            subprocess.run(
                ['adb', '-s', self.device_id, 'shell', 'screencap', '-p', device_path],
                check=True
            )
            
            # Pull screenshot from device
            subprocess.run(
                ['adb', '-s', self.device_id, 'pull', device_path, output_path],
                check=True
            )
            
            # Remove screenshot from device
            subprocess.run(
                ['adb', '-s', self.device_id, 'shell', 'rm', device_path],
                check=True
            )
            
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Error taking screenshot: {e}")
            return False
    
    def get_screen_dimensions(self) -> Tuple[int, int]:
        """
        Get the screen dimensions of the device.
        
        Returns:
            Tuple containing the width and height of the screen.
        """
        if not self.connected:
            logger.warning(f"Device {self.device_id} is not connected")
            return (0, 0)
        
        try:
            result = subprocess.run(
                ['adb', '-s', self.device_id, 'shell', 'wm', 'size'],
                capture_output=True,
                text=True,
                check=True
            )
            
            match = re.search(r'Physical size: (\d+)x(\d+)', result.stdout)
            if match:
                width = int(match.group(1))
                height = int(match.group(2))
                return (width, height)
            
            return (0, 0)
        except subprocess.CalledProcessError as e:
            logger.error(f"Error getting screen dimensions: {e}")
            return (0, 0)
    
    def tap(self, x: int, y: int) -> bool:
        """
        Tap on the screen at the specified coordinates.
        
        Args:
            x: X coordinate.
            y: Y coordinate.
            
        Returns:
            True if the tap was successful, False otherwise.
        """
        if not self.connected:
            logger.warning(f"Device {self.device_id} is not connected")
            return False
        
        logger.info(f"Tapping at ({x}, {y}) on device {self.device_id}")
        
        try:
            subprocess.run(
                ['adb', '-s', self.device_id, 'shell', 'input', 'tap', str(x), str(y)],
                check=True
            )
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Error tapping: {e}")
            return False
    
    def swipe(self, start_x: int, start_y: int, end_x: int, end_y: int, duration_ms: int = 500) -> bool:
        """
        Swipe on the screen from the start coordinates to the end coordinates.
        
        Args:
            start_x: Starting X coordinate.
            start_y: Starting Y coordinate.
            end_x: Ending X coordinate.
            end_y: Ending Y coordinate.
            duration_ms: Duration of the swipe in milliseconds.
            
        Returns:
            True if the swipe was successful, False otherwise.
        """
        if not self.connected:
            logger.warning(f"Device {self.device_id} is not connected")
            return False
        
        logger.info(f"Swiping from ({start_x}, {start_y}) to ({end_x}, {end_y}) on device {self.device_id}")
        
        try:
            subprocess.run(
                ['adb', '-s', self.device_id, 'shell', 'input', 'swipe', 
                 str(start_x), str(start_y), str(end_x), str(end_y), str(duration_ms)],
                check=True
            )
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Error swiping: {e}")
            return False
    
    def input_text(self, text: str) -> bool:
        """
        Input text on the device.
        
        Args:
            text: Text to input.
            
        Returns:
            True if the text input was successful, False otherwise.
        """
        if not self.connected:
            logger.warning(f"Device {self.device_id} is not connected")
            return False
        
        logger.info(f"Inputting text on device {self.device_id}")
        
        try:
            # Escape special characters
            escaped_text = text.replace(' ', '%s').replace('&', '\\&').replace('<', '\\<').replace('>', '\\>')
            
            subprocess.run(
                ['adb', '-s', self.device_id, 'shell', 'input', 'text', escaped_text],
                check=True
            )
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Error inputting text: {e}")
            return False
    
    def press_key(self, key_code: int) -> bool:
        """
     
(Content truncated due to size limit. Use line ranges to read in chunks)