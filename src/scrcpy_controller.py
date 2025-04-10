"""
Scrcpy Controller module for AI QA Agent.
This module provides functionality for controlling Android devices using scrcpy.
"""
import os
import logging
import subprocess
import time
import signal
import tempfile
import atexit
from typing import Dict, List, Any, Optional, Tuple, Union

logger = logging.getLogger(__name__)

class ScrcpyController:
    """Class for controlling Android devices using scrcpy."""
    
    def __init__(self, device_id: Optional[str] = None):
        """
        Initialize the Scrcpy Controller.
        
        Args:
            device_id: Optional device ID. If not provided, will use the first available device.
        """
        self.device_id = device_id
        self.process = None
        self.recording_process = None
        self.recording_file = None
        
        # Register cleanup handler
        atexit.register(self.cleanup)
        
        logger.info(f"Initialized Scrcpy Controller for device: {self.device_id}")
    
    def start_mirroring(self, window_title: Optional[str] = None, 
                       window_width: Optional[int] = None, 
                       window_height: Optional[int] = None,
                       no_control: bool = False,
                       stay_awake: bool = True,
                       fullscreen: bool = False) -> bool:
        """
        Start mirroring the device screen using scrcpy.
        
        Args:
            window_title: Optional window title. If not provided, will use default.
            window_width: Optional window width. If not provided, will use default.
            window_height: Optional window height. If not provided, will use default.
            no_control: Whether to disable device control.
            stay_awake: Whether to keep the device awake while mirroring.
            fullscreen: Whether to start in fullscreen mode.
            
        Returns:
            True if mirroring was started successfully, False otherwise.
        """
        if self.process:
            logger.warning("Scrcpy is already running")
            return False
        
        logger.info(f"Starting scrcpy for device {self.device_id}")
        
        try:
            cmd = ['scrcpy']
            
            # Add device ID if provided
            if self.device_id:
                cmd.extend(['--serial', self.device_id])
            
            # Add window title if provided
            if window_title:
                cmd.extend(['--window-title', window_title])
            
            # Add window dimensions if provided
            if window_width and window_height:
                cmd.extend(['--max-size', f'{window_width}'])
                
            # Add other options
            if no_control:
                cmd.append('--no-control')
            
            if stay_awake:
                cmd.append('--stay-awake')
            
            if fullscreen:
                cmd.append('--fullscreen')
            
            # Start scrcpy process
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait a bit to ensure scrcpy starts
            time.sleep(2)
            
            # Check if process is still running
            if self.process.poll() is not None:
                stderr = self.process.stderr.read()
                logger.error(f"Scrcpy failed to start: {stderr}")
                self.process = None
                return False
            
            logger.info("Scrcpy started successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error starting scrcpy: {e}")
            return False
    
    def stop_mirroring(self) -> bool:
        """
        Stop mirroring the device screen.
        
        Returns:
            True if mirroring was stopped successfully, False otherwise.
        """
        if not self.process:
            logger.warning("Scrcpy is not running")
            return False
        
        logger.info("Stopping scrcpy")
        
        try:
            # Terminate the process
            self.process.terminate()
            
            # Wait for process to terminate
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                # Force kill if it doesn't terminate
                self.process.kill()
            
            self.process = None
            
            logger.info("Scrcpy stopped successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error stopping scrcpy: {e}")
            return False
    
    def start_recording(self, output_file: Optional[str] = None, 
                       bit_rate: int = 8000000) -> bool:
        """
        Start recording the device screen using scrcpy.
        
        Args:
            output_file: Optional output file path. If not provided, will use a temporary file.
            bit_rate: Bit rate for the recording in bits per second.
            
        Returns:
            True if recording was started successfully, False otherwise.
        """
        if self.recording_process:
            logger.warning("Recording is already in progress")
            return False
        
        # If no output file provided, create a temporary file
        if not output_file:
            fd, output_file = tempfile.mkstemp(suffix='.mp4')
            os.close(fd)
        
        self.recording_file = output_file
        
        logger.info(f"Starting screen recording to {output_file}")
        
        try:
            cmd = ['scrcpy', '--no-display', '--record', output_file, '--bit-rate', str(bit_rate)]
            
            # Add device ID if provided
            if self.device_id:
                cmd.extend(['--serial', self.device_id])
            
            # Start recording process
            self.recording_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait a bit to ensure recording starts
            time.sleep(2)
            
            # Check if process is still running
            if self.recording_process.poll() is not None:
                stderr = self.recording_process.stderr.read()
                logger.error(f"Recording failed to start: {stderr}")
                self.recording_process = None
                self.recording_file = None
                return False
            
            logger.info("Recording started successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error starting recording: {e}")
            self.recording_file = None
            return False
    
    def stop_recording(self) -> Optional[str]:
        """
        Stop recording the device screen.
        
        Returns:
            Path to the recording file if recording was stopped successfully, None otherwise.
        """
        if not self.recording_process:
            logger.warning("Recording is not in progress")
            return None
        
        logger.info("Stopping screen recording")
        
        try:
            # Send SIGINT to gracefully terminate and save the recording
            self.recording_process.send_signal(signal.SIGINT)
            
            # Wait for process to terminate
            try:
                self.recording_process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                # Force kill if it doesn't terminate
                self.recording_process.kill()
                logger.warning("Had to force kill recording process")
            
            recording_file = self.recording_file
            self.recording_process = None
            self.recording_file = None
            
            logger.info(f"Recording stopped successfully: {recording_file}")
            return recording_file
            
        except Exception as e:
            logger.error(f"Error stopping recording: {e}")
            return None
    
    def is_mirroring(self) -> bool:
        """
        Check if mirroring is active.
        
        Returns:
            True if mirroring is active, False otherwise.
        """
        return self.process is not None and self.process.poll() is None
    
    def is_recording(self) -> bool:
        """
        Check if recording is active.
        
        Returns:
            True if recording is active, False otherwise.
        """
        return self.recording_process is not None and self.recording_process.poll() is None
    
    def cleanup(self) -> None:
        """Clean up resources when the object is destroyed."""
        logger.info("Cleaning up Scrcpy Controller resources")
        
        if self.is_mirroring():
            self.stop_mirroring()
        
        if self.is_recording():
            self.stop_recording()
