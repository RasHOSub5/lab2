"""
Loading Animation Module

This module provides a visual loading indicator for console applications.
It runs in a separate thread to provide feedback during long-running operations.
"""

import sys
import time
from threading import Thread, Event

class LoadingAnimation:
    """
    A thread-safe loading animation for console applications.
    
    This class provides a simple animated loading indicator that runs in a separate
    thread, allowing the main thread to continue processing while showing progress.
    
    Attributes:
        message (str): The message to display with the animation
        animation_frames (list): Characters to cycle through for the animation
        
    Example:
        >>> loader = LoadingAnimation("Processing")
        >>> loader.start()
        >>> # Do some work...
        >>> loader.stop(True)  # Stops with success
    """
    
    def __init__(self, message="Loading"):
        """Initialize the loading animation.
        
        Args:
            message (str): The message to display with the animation
        """
        self._message = message
        self._stop_event = Event()
        self.animation_thread = None
        self.animation_frames = ['|', '/', '-', '\\']  # Rotating animation frames
        self._lock = False  # Prevents message changes during critical sections
        
    @property
    def message(self):
        """Get the current message being displayed."""
        return self._message
        
    @message.setter
    def message(self, value):
        """Update the message being displayed.
        
        Args:
            value (str): New message to display
            
        Note:
            Message updates won't take effect if the animation is locked
            during critical operations.
        """
        if not self._lock:
            self._message = value
        
    def _animate(self):
        """Internal method that handles the animation loop.
        
        This method runs in a separate thread and continuously updates
        the console with the current animation frame.
        """
        frame_index = 0
        last_output = ""
        
        while not self._stop_event.is_set():
            # Build the output string with current animation frame
            output = f"{self.message} {self.animation_frames[frame_index]}"
            
            # Only update if the output has changed to reduce flickering
            if output != last_output:
                # Calculate padding to properly clear the previous output
                padding = max(0, len(last_output) - len(output))
                
                # Use carriage return to overwrite the current line
                # Add padding to clear any remaining characters from previous output
                sys.stdout.write('\r' + output + ' ' * padding + '\r' + output)
                sys.stdout.flush()
                last_output = output
            
            # Move to next frame, wrapping around if needed
            frame_index = (frame_index + 1) % len(self.animation_frames)
            time.sleep(0.15)  # Control animation speed
        
    def start(self):
        """Start the loading animation in a separate thread.
        
        Creates and starts a daemon thread that runs the animation.
        The animation will continue until stop() is called.
        """
        self._stop_event.clear()
        self.animation_thread = Thread(target=self._animate)
        self.animation_thread.daemon = True  # Allow program to exit even if thread is running
        self.animation_thread.start()
        
    def stop(self, success=True):
        """Stop the loading animation and display final status.
        
        Args:
            success (bool): Whether the operation completed successfully.
                          Affects the status indicator (✓ for success, ✗ for failure).
        """
        # Signal the animation thread to stop
        self._stop_event.set()
        
        # Wait for the animation thread to finish
        if self.animation_thread:
            self.animation_thread.join()
        
        # Determine status indicator
        status = "✓" if success else "✗"
        
        # Clear the current line and print the final status
        # \r - Return to start of line
        # \033[K - Clear to end of line
        sys.stdout.write('\r\033[K')
        sys.stdout.write(f'{self.message} {status}\n')
        sys.stdout.flush()

# Example usage:
if __name__ == "__main__":
    loader = LoadingAnimation("Processing")
    loader.start()
    
    # Simulate some work
    time.sleep(3)
    
    # Stop with success
    loader.stop(True)
    
    # Or with error
    # loader.stop(False)
