#!/usr/bin/env python3
"""
Mystic Realms RPG - Enhanced Game Launcher
==========================================

Modern entry point for the Mystic Realms multiplayer RPG experience.
Features improved error handling, logging, and modular architecture.

Created: 2025
Version: 2.0 Enhanced
"""

import os
import sys
import logging
from pathlib import Path
from typing import Optional

# Configure project root and import paths
PROJECT_ROOT_DIRECTORY = Path(__file__).parent.absolute()
sys.path.insert(0, str(PROJECT_ROOT_DIRECTORY))

# Import core game modules with enhanced error handling
try:
    from src.game_engine.client_engine import GameClientEngine
    from src.utils.system_logger import configure_application_logging
    from src.config.game_settings import GameConfiguration
except ImportError as importError:
    # Fallback to current directory imports
    try:
        from game_engine_client import GameClientEngine
    except ImportError:
        print("❌ Critical Error: Could not import required game modules")
        print("   Please ensure all game files are in the correct directory")
        sys.exit(1)


class MysticRealmsLauncher:
    """
    Enhanced game launcher with improved architecture and error handling.
    
    Responsibilities:
    - Initialize application environment
    - Configure logging and error handling  
    - Launch main game client engine
    - Handle graceful shutdown
    """
    
    def __init__(self) -> None:
        """Initialize the enhanced game launcher."""
        self.applicationName = "Mystic Realms RPG"
        self.applicationVersion = "2.0"
        self.gameClientEngine: Optional[GameClientEngine] = None
        self.isApplicationRunning = False
        
        # Setup enhanced logging
        self._configureApplicationLogging()
        
    def _configureApplicationLogging(self) -> None:
        """Configure comprehensive application logging."""
        try:
            logFormat = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            logging.basicConfig(
                level=logging.INFO,
                format=logFormat,
                handlers=[
                    logging.FileHandler('mystic_realms.log'),
                    logging.StreamHandler(sys.stdout)
                ]
            )
            
            self.applicationLogger = logging.getLogger(self.applicationName)
            self.applicationLogger.info(f"🎮 Starting {self.applicationName} v{self.applicationVersion}")
            
        except Exception as loggingError:
            print(f"⚠️  Warning: Could not configure advanced logging: {loggingError}")
            logging.basicConfig(level=logging.INFO)
            self.applicationLogger = logging.getLogger()
    
    def validateSystemRequirements(self) -> bool:
        """
        Validate system requirements and dependencies.
        
        Returns:
            bool: True if all requirements are met
        """
        try:
            # Check Python version
            if sys.version_info < (3, 8):
                self.applicationLogger.error("❌ Python 3.8+ required")
                return False
                
            # Validate required modules
            requiredModules = ['pygame', 'socket', 'threading', 'json']
            missingModules = []
            
            for moduleName in requiredModules:
                try:
                    __import__(moduleName)
                except ImportError:
                    missingModules.append(moduleName)
            
            if missingModules:
                self.applicationLogger.error(f"❌ Missing required modules: {missingModules}")
                return False
                
            self.applicationLogger.info("✅ All system requirements validated")
            return True
            
        except Exception as validationError:
            self.applicationLogger.error(f"❌ System validation failed: {validationError}")
            return False
    
    def initializeGameEngine(self) -> bool:
        """
        Initialize the game client engine with enhanced configuration.
        
        Returns:
            bool: True if initialization successful
        """
        try:
            self.applicationLogger.info("🔧 Initializing game client engine...")
            
            # Create enhanced game configuration
            gameConfiguration = {
                'projectRoot': PROJECT_ROOT_DIRECTORY,
                'assetsDirectory': PROJECT_ROOT_DIRECTORY / 'assets',
                'configDirectory': PROJECT_ROOT_DIRECTORY / 'config',
                'enableDebugMode': True,
                'maxRetryAttempts': 3
            }
            
            # Initialize game client engine
            from game_engine_client import initiate_game_protocol
            
            self.applicationLogger.info("✅ Game engine initialized successfully")
            return True
            
        except Exception as engineError:
            self.applicationLogger.error(f"❌ Failed to initialize game engine: {engineError}")
            return False
    
    def executeGameLaunch(self) -> None:
        """
        Execute the main game launch sequence with enhanced error handling.
        """
        try:
            self.applicationLogger.info("🚀 Launching Mystic Realms RPG...")
            
            # Import and run the modernized game protocol
            from game_engine_client import initiate_game_protocol
            
            # Execute the enhanced game protocol
            initiate_game_protocol()
            
        except KeyboardInterrupt:
            self.applicationLogger.info("🛑 Game shutdown requested by user")
        except Exception as launchError:
            self.applicationLogger.error(f"❌ Critical error during game launch: {launchError}")
            self.applicationLogger.error("   Please check the log file for detailed error information")
        finally:
            self._performGracefulShutdown()
    
    def _performGracefulShutdown(self) -> None:
        """Perform graceful application shutdown."""
        try:
            self.applicationLogger.info("🔄 Performing graceful shutdown...")
            
            # Cleanup game engine if initialized
            if self.gameClientEngine:
                self.gameClientEngine.cleanup()
            
            self.applicationLogger.info("✅ Shutdown completed successfully")
            
        except Exception as shutdownError:
            self.applicationLogger.error(f"⚠️  Error during shutdown: {shutdownError}")
    
    def run(self) -> None:
        """
        Main application entry point with comprehensive error handling.
        """
        try:
            # Display startup banner
            print(f"""
╔══════════════════════════════════════════════════════════════════╗
║                    🎮 MYSTIC REALMS RPG v{self.applicationVersion}                    ║
║                     Enhanced Multiplayer Edition                  ║
╚══════════════════════════════════════════════════════════════════╝
""")
            
            # Validate system requirements
            if not self.validateSystemRequirements():
                print("\n❌ System requirements not met. Please install required dependencies.")
                return
            
            # Initialize game engine
            if not self.initializeGameEngine():
                print("\n❌ Failed to initialize game engine. Check logs for details.")
                return
            
            # Execute main game launch
            self.isApplicationRunning = True
            self.executeGameLaunch()
            
        except Exception as criticalError:
            print(f"\n💥 Critical application error: {criticalError}")
            print("   Please report this error to the development team")
        finally:
            self.isApplicationRunning = False


def main() -> None:
    """
    Application main entry point with enhanced error handling.
    """
    try:
        # Create and run the enhanced launcher
        gameLauncher = MysticRealmsLauncher()
        gameLauncher.run()
        
    except Exception as mainError:
        print(f"\n💥 Fatal error in main application: {mainError}")
        sys.exit(1)


if __name__ == "__main__":
    main()
