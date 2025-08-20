#!/usr/bin/env python3
"""
Mystic Realms - Enhanced Game Client Engine
===========================================

Modern game client with improved architecture, better performance,
and enhanced user experience features.

Key Features:
- Modular component architecture
- Enhanced visual effects and UI
- Optimized rendering pipeline
- Thread-safe networking
- Comprehensive error handling
- Modern input handling system

Created: 2025
Version: 2.0 Enhanced
"""

import pygame as pg
import json
import tkinter as tk
from tkinter import messagebox, font, ttk
import random
import threading
import time
import pytmx
import math
import sys
import os
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager

# Import enhanced modules
from src.entities import enhanced_player_model
from src.network import enhanced_client_socket
from src.ui import modern_authentication_interface
from src.audio import advanced_sound_manager
from src.graphics import optimized_renderer
from src.utils import performance_monitor


@dataclass
class GameConfiguration:
    """Enhanced game configuration with modern defaults."""
    screenResolution: Tuple[int, int] = (1000, 650)
    targetFrameRate: int = 60
    audioVolume: float = 0.7
    enableVsync: bool = True
    enableAntiAliasing: bool = True
    renderQuality: str = "HIGH"
    networkTimeout: float = 5.0
    maxRetryAttempts: int = 3


@dataclass
class PlayerState:
    """Enhanced player state management."""
    worldPosition: Tuple[int, int] = (3000, 11000)
    dimensions: Tuple[int, int] = (60, 60)
    currentHealth: int = 100
    maxHealth: int = 100
    playerId: int = 0
    selectedWeaponIndex: int = 0
    movementDirection: str = ""
    isMoving: bool = False


@dataclass
class WeaponConfiguration:
    """Modern weapon system configuration."""
    weaponName: str
    damagePoints: int
    effectiveRange: int
    projectileVelocity: int
    currentAmmunition: int
    maximumAmmunition: int
    weaponIdentifier: int


class GameStateManager:
    """Thread-safe game state management with enhanced features."""
    
    def __init__(self):
        self.gameStateData = {
            "explosiveActivated": False,
            "selectedWeapon": 0,
            "playerHitByProjectile": False,
            "movementOffset": (0, 0),
            "secondaryMovementOffset": (0, 0),
            "incomingNetworkData": {}
        }
        self.stateLock = threading.RLock()
    
    @contextmanager
    def thread_safe_access(self):
        """Context manager for thread-safe state access."""
        with self.stateLock:
            yield self.gameStateData
    
    def updateGameState(self, stateKey: str, newValue: Any) -> None:
        """Thread-safe game state update."""
        with self.stateLock:
            self.gameStateData[stateKey] = newValue
    
    def getGameState(self, stateKey: str) -> Any:
        """Thread-safe game state retrieval."""
        with self.stateLock:
            return self.gameStateData.get(stateKey)


class EnhancedGameClient:
    """
    Modern game client with improved architecture and performance.
    
    Features:
    - Component-based architecture
    - Enhanced networking with connection pooling
    - Optimized rendering pipeline
    - Advanced input handling
    - Comprehensive error recovery
    """
    
    def __init__(self, configuration: Optional[GameConfiguration] = None):
        """Initialize the enhanced game client."""
        
        # Core configuration
        self.gameConfig = configuration or GameConfiguration()
        self.gameStateManager = GameStateManager()
        
        # Enhanced logging system
        self._configureClientLogging()
        
        # Initialize pygame with enhanced settings
        self._initializeEnhancedPygame()
        
        # Core game components
        self.networkManager: Optional[enhanced_client_socket.EnhancedClientSocket] = None
        self.audioManager = advanced_sound_manager.AdvancedSoundManager()
        self.renderingEngine = optimized_renderer.OptimizedRenderer(self.gameScreen)
        self.performanceMonitor = performance_monitor.PerformanceMonitor()
        
        # Game state and entities
        self.playerState = PlayerState()
        self.connectedPlayers: Dict[int, Dict] = {}
        self.activeNpcs: Dict[int, Dict] = {}
        self.weaponConfigurations = self._initializeWeaponSystem()
        
        # UI and visual components
        self.inventorySystem = self._initializeInventorySystem()
        self.chatInterface = self._initializeChatInterface()
        
        # Threading and performance
        self.threadPoolExecutor = ThreadPoolExecutor(max_workers=8)
        self.isGameRunning = False
        
        # Enhanced map system
        self.gameWorldMap: Optional[pytmx.TiledMap] = None
        self.mapRenderingSurface: Optional[pg.Surface] = None
        
        self.logger.info("✅ Enhanced game client initialized")
    
    def _configureClientLogging(self) -> None:
        """Configure comprehensive client logging."""
        logFormat = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        logging.basicConfig(
            level=logging.INFO,
            format=logFormat,
            handlers=[
                logging.FileHandler('mystic_realms_client.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger("EnhancedGameClient")
    
    def _initializeEnhancedPygame(self) -> None:
        """Initialize pygame with enhanced settings and error handling."""
        try:
            pg.init()
            pg.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            
            # Enhanced display settings
            displayFlags = pg.DOUBLEBUF | pg.HWSURFACE
            if self.gameConfig.enableVsync:
                displayFlags |= pg.VSYNC
                
            self.gameScreen = pg.display.set_mode(
                self.gameConfig.screenResolution, 
                displayFlags
            )
            pg.display.set_caption("Mystic Realms RPG - Enhanced Edition")
            
            # Enhanced font system
            self.uiFonts = {
                'fps_display': pg.font.SysFont('Arial', 32, bold=True),
                'chat_text': pg.font.SysFont('Consolas', 20),
                'ui_elements': pg.font.SysFont('Arial', 24),
                'damage_numbers': pg.font.SysFont('Impact', 28, bold=True)
            }
            
            self.gameClock = pg.time.Clock()
            self.logger.info("✅ Enhanced pygame initialization completed")
            
        except Exception as pygameError:
            self.logger.error(f"❌ Failed to initialize pygame: {pygameError}")
            raise
    
    def _initializeWeaponSystem(self) -> List[WeaponConfiguration]:
        """Initialize enhanced weapon system with modern configuration."""
        return [
            WeaponConfiguration("Plasma Rifle", 25, 10000, 70, 50, 50, 1),
            WeaponConfiguration("Quantum Sniper", 35, 70000, 80, 20, 20, 2),
            WeaponConfiguration("Fusion Cannon", 45, 120000, 100, 7, 7, 3)
        ]
    
    def _initializeInventorySystem(self) -> Dict:
        """Initialize enhanced inventory system."""
        inventorySlotSize = 50
        scriptDirectory = Path(__file__).parent
        
        def loadWeaponIcon(filename: str) -> pg.Surface:
            iconPath = scriptDirectory / "assets" / "weapons" / filename
            if not iconPath.exists():
                iconPath = scriptDirectory / filename  # Fallback
            
            weaponIcon = pg.image.load(str(iconPath)).convert_alpha()
            return pg.transform.scale(weaponIcon, (inventorySlotSize - 10, inventorySlotSize - 10))
        
        weaponIcons = [
            loadWeaponIcon("plasma_rifle_icon.png"),
            loadWeaponIcon("quantum_sniper_icon.png"), 
            loadWeaponIcon("fusion_cannon_icon.png")
        ]
        
        inventorySlots = [
            {"itemName": f"weapon_{i+1}", "iconImage": icon, "quantity": 1}
            for i, icon in enumerate(weaponIcons)
        ] + [None] * 7
        
        return {
            'slots': inventorySlots,
            'selectedSlot': 0,
            'slotSize': inventorySlotSize
        }
    
    def _initializeChatInterface(self) -> Dict:
        """Initialize enhanced chat interface."""
        return {
            'messageHistory': [],
            'currentInput': "",
            'isInputActive': False,
            'maxVisibleMessages': 5
        }
    
    def establishNetworkConnection(self) -> bool:
        """Establish enhanced network connection with improved error handling."""
        try:
            self.logger.info("🔗 Establishing network connection...")
            
            self.networkManager = enhanced_client_socket.EnhancedClientSocket()
            connectionResult = self.networkManager.establishConnection()
            
            if connectionResult:
                self.logger.info("✅ Network connection established")
                return True
            else:
                self.logger.error("❌ Failed to establish network connection")
                return False
                
        except Exception as networkError:
            self.logger.error(f"❌ Network connection error: {networkError}")
            return False
    
    def launchAuthenticationInterface(self) -> Optional[Dict]:
        """Launch modern authentication interface."""
        try:
            authenticationWindow = tk.Tk()
            authInterface = modern_authentication_interface.ModernAuthenticationInterface(
                authenticationWindow, 
                self.networkManager
            )
            
            authenticationWindow.title("Mystic Realms - Player Authentication")
            authenticationWindow.mainloop()
            
            if authInterface.authenticationData:
                self.logger.info("✅ Player authentication successful")
                return authInterface.authenticationData
            else:
                self.logger.warning("⚠️ Player authentication cancelled")
                return None
                
        except Exception as authError:
            self.logger.error(f"❌ Authentication interface error: {authError}")
            return None
    
    def initializeGameWorld(self) -> bool:
        """Initialize enhanced game world with optimized loading."""
        try:
            self.logger.info("🌍 Loading game world...")
            
            # Load enhanced map system
            projectDirectory = Path(__file__).parent
            mapFilePath = projectDirectory / "assets" / "maps" / "enhanced_world.tmx"
            
            if not mapFilePath.exists():
                mapFilePath = projectDirectory / "map" / "map.tmx"  # Fallback
            
            if mapFilePath.exists():
                self.gameWorldMap = pytmx.load_pygame(str(mapFilePath), pixelalpha=True)
                self.logger.info(f"✅ Game world loaded: {mapFilePath.name}")
                
                # Initialize optimized map rendering
                self._initializeOptimizedMapRendering()
                return True
            else:
                self.logger.error("❌ Game world map file not found")
                return False
                
        except Exception as worldError:
            self.logger.error(f"❌ Failed to initialize game world: {worldError}")
            return False
    
    def _initializeOptimizedMapRendering(self) -> None:
        """Initialize optimized map rendering system."""
        if self.gameWorldMap:
            mapRenderingThread = threading.Thread(
                target=self._continuousMapRendering,
                name="OptimizedMapRenderer",
                daemon=True
            )
            mapRenderingThread.start()
    
    def _continuousMapRendering(self) -> None:
        """Continuous optimized map rendering in separate thread."""
        while self.isGameRunning:
            try:
                if self.gameWorldMap:
                    newMapSurface = self.renderingEngine.renderMapSurface(
                        self.gameWorldMap,
                        self.playerState.worldPosition,
                        self.gameConfig.screenResolution
                    )
                    
                    with self.gameStateManager.thread_safe_access():
                        self.mapRenderingSurface = newMapSurface
                
                time.sleep(1.0 / 30)  # 30 FPS for map rendering
                
            except Exception as renderError:
                self.logger.error(f"❌ Map rendering error: {renderError}")
                time.sleep(1.0)
    
    def processExplosiveEffects(self) -> None:
        """Process enhanced explosive effects with improved visuals."""
        while self.isGameRunning:
            try:
                with self.gameStateManager.thread_safe_access() as gameState:
                    if gameState["explosiveActivated"]:
                        self._executeExplosiveSequence()
                        gameState["explosiveActivated"] = False
                    
                    # Process incoming explosive effects
                    for entityId, entityData in list(gameState["incomingNetworkData"].items()):
                        if 'explosive_effect' in entityData:
                            self._renderIncomingExplosive(entityData['explosive_effect'])
                            del gameState["incomingNetworkData"][entityId]
                
                time.sleep(0.02)  # High frequency for smooth effects
                
            except Exception as explosiveError:
                self.logger.error(f"❌ Explosive effects error: {explosiveError}")
    
    def _executeExplosiveSequence(self) -> None:
        """Execute enhanced explosive visual sequence."""
        explosionCenter = (
            self.playerState.worldPosition[0] - self.playerState.worldPosition[0] + 500,
            self.playerState.worldPosition[1] - self.playerState.worldPosition[1] + 325
        )
        
        explosionRadius = 200
        explosionColor = (255, 100, 0)  # Orange explosion
        
        # Enhanced explosion rendering
        explosionSurface = pg.Surface(self.gameConfig.screenResolution, pg.SRCALPHA)
        pg.draw.circle(explosionSurface, explosionColor, explosionCenter, explosionRadius)
        
        self.gameScreen.blit(explosionSurface, (0, 0))
        pg.display.flip()
        
        # Send explosion data to server
        if self.networkManager:
            self.networkManager.sendExplosiveActivation(
                self.playerState.worldPosition[0],
                self.playerState.worldPosition[1],
                explosionRadius
            )
    
    def executeEnhancedCombatSystem(self, targetPosition: Tuple[int, int]) -> None:
        """Execute enhanced combat system with improved projectile physics."""
        selectedWeapon = self.weaponConfigurations[self.playerState.selectedWeaponIndex]
        
        if selectedWeapon.currentAmmunition <= 0:
            self.logger.warning("⚠️ Insufficient ammunition")
            return
        
        # Enhanced projectile calculation
        projectileStartPosition = list(pg.mouse.get_pos())
        projectileDirection = self._calculateProjectileTrajectory(projectileStartPosition, targetPosition)
        
        # Create enhanced projectile thread
        combatThread = threading.Thread(
            target=self._processEnhancedProjectile,
            args=(selectedWeapon, projectileDirection, targetPosition),
            name="EnhancedCombat"
        )
        combatThread.start()
        
        # Update ammunition
        selectedWeapon.currentAmmunition -= 1
        
        # Play enhanced audio
        self.audioManager.playWeaponSound(selectedWeapon.weaponName)
    
    def _calculateProjectileTrajectory(self, startPos: List[int], targetPos: Tuple[int, int]) -> Dict:
        """Calculate enhanced projectile trajectory with physics."""
        startPos[0] -= 500
        startPos[1] = 325 - startPos[1]
        
        if startPos[0] != 0:
            trajectorySlope = startPos[1] / startPos[0]
            trajectoryAngle = math.degrees(math.atan(trajectorySlope))
        else:
            trajectoryAngle = 90 if startPos[1] > 0 else -90
        
        return {
            'startPosition': startPos,
            'angle': trajectoryAngle,
            'targetPosition': targetPos
        }
    
    def _processEnhancedProjectile(self, weapon: WeaponConfiguration, trajectory: Dict, target: Tuple[int, int]) -> None:
        """Process enhanced projectile with improved collision detection."""
        projectileImage = self.renderingEngine.createProjectileSprite()
        projectileHit = False
        currentRange = 1
        
        while currentRange < weapon.effectiveRange and not projectileHit:
            # Enhanced projectile movement calculation
            currentRange += weapon.projectileVelocity
            
            # Update projectile position
            projectilePosition = self._updateProjectilePosition(trajectory, currentRange)
            
            # Enhanced collision detection
            projectileHit = self._checkEnhancedCollisions(projectilePosition, weapon.damagePoints)
            
            # Render projectile
            self.renderingEngine.renderProjectile(projectileImage, projectilePosition)
            
            time.sleep(0.01)  # Smooth projectile movement
    
    def executeMainGameLoop(self) -> None:
        """Execute the main enhanced game loop with optimized performance."""
        self.isGameRunning = True
        
        # Start background systems
        self._startBackgroundSystems()
        
        try:
            while self.isGameRunning:
                frameStartTime = time.time()
                
                # Process user input
                self._processEnhancedInput()
                
                # Update game state
                self._updateGameState()
                
                # Render enhanced graphics
                self._renderEnhancedFrame()
                
                # Performance monitoring
                self.performanceMonitor.recordFrameTime(time.time() - frameStartTime)
                
                # Maintain target frame rate
                self.gameClock.tick(self.gameConfig.targetFrameRate)
                
        except KeyboardInterrupt:
            self.logger.info("🛑 Game shutdown requested")
        except Exception as gameLoopError:
            self.logger.error(f"❌ Game loop error: {gameLoopError}")
        finally:
            self._performGameCleanup()
    
    def _startBackgroundSystems(self) -> None:
        """Start enhanced background systems."""
        # Explosive effects system
        explosiveThread = threading.Thread(
            target=self.processExplosiveEffects,
            name="ExplosiveEffects",
            daemon=True
        )
        explosiveThread.start()
        
        # Network data processing
        networkThread = threading.Thread(
            target=self._processNetworkData,
            name="NetworkProcessor", 
            daemon=True
        )
        networkThread.start()
    
    def _processEnhancedInput(self) -> None:
        """Process enhanced user input with modern handling."""
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.isGameRunning = False
            
            elif event.type == pg.KEYDOWN:
                self._handleKeyboardInput(event)
            
            elif event.type == pg.MOUSEBUTTONDOWN:
                self._handleMouseInput(event)
            
            elif event.type == pg.MOUSEMOTION:
                self._handleMouseMovement(event)
    
    def _renderEnhancedFrame(self) -> None:
        """Render enhanced frame with optimized graphics."""
        # Clear screen with enhanced background
        self.gameScreen.fill((20, 25, 40))  # Dark blue background
        
        # Render optimized map
        if self.mapRenderingSurface:
            self.gameScreen.blit(self.mapRenderingSurface, (0, 0))
        
        # Render game entities
        self.renderingEngine.renderGameEntities(
            self.connectedPlayers,
            self.activeNpcs,
            self.playerState
        )
        
        # Render enhanced UI
        self._renderEnhancedUI()
        
        # Update display
        pg.display.flip()
    
    def _renderEnhancedUI(self) -> None:
        """Render enhanced user interface elements."""
        # FPS display with enhanced styling
        currentFps = self.gameClock.get_fps()
        fpsColor = (0, 255, 0) if currentFps > 50 else (255, 255, 0) if currentFps > 30 else (255, 0, 0)
        fpsText = self.uiFonts['fps_display'].render(f"FPS: {currentFps:.1f}", True, fpsColor)
        self.gameScreen.blit(fpsText, (10, 10))
        
        # Enhanced health bar
        self.renderingEngine.renderEnhancedHealthBar(
            self.gameScreen, 
            (10, 50), 
            self.playerState.currentHealth, 
            self.playerState.maxHealth
        )
        
        # Enhanced ammunition display
        selectedWeapon = self.weaponConfigurations[self.playerState.selectedWeaponIndex]
        ammoText = self.uiFonts['ui_elements'].render(
            f"Ammo: {selectedWeapon.currentAmmunition}/{selectedWeapon.maximumAmmunition}", 
            True, 
            (255, 255, 255)
        )
        self.gameScreen.blit(ammoText, (10, 90))
        
        # Enhanced inventory hotbar
        self.renderingEngine.renderEnhancedInventory(
            self.gameScreen,
            self.inventorySystem['selectedSlot'],
            self.inventorySystem['slots']
        )
    
    def _performGameCleanup(self) -> None:
        """Perform comprehensive game cleanup."""
        self.logger.info("🧹 Performing game cleanup...")
        
        self.isGameRunning = False
        
        if self.networkManager:
            self.networkManager.closeConnection()
        
        self.threadPoolExecutor.shutdown(wait=True)
        pg.quit()
        
        self.logger.info("✅ Game cleanup completed")


def initiate_game_protocol() -> None:
    """
    Main game protocol with enhanced error handling and modern architecture.
    """
    logger = logging.getLogger("GameProtocol")
    
    try:
        # Create enhanced game client
        gameConfiguration = GameConfiguration()
        enhancedClient = EnhancedGameClient(gameConfiguration)
        
        # Establish network connection
        if not enhancedClient.establishNetworkConnection():
            logger.error("❌ Failed to establish network connection")
            return
        
        # Launch authentication interface
        authenticationData = enhancedClient.launchAuthenticationInterface()
        if not authenticationData:
            logger.warning("⚠️ Authentication cancelled by user")
            return
        
        # Initialize game world
        if not enhancedClient.initializeGameWorld():
            logger.error("❌ Failed to initialize game world")
            return
        
        # Execute main game loop
        enhancedClient.executeMainGameLoop()
        
    except Exception as protocolError:
        logger.error(f"❌ Critical error in game protocol: {protocolError}")
    
    logger.info("✅ Game protocol completed")


if __name__ == "__main__":
    initiate_game_protocol()
