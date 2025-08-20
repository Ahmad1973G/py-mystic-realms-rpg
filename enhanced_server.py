#!/usr/bin/env python3
"""
Mystic Realms - Enhanced Server Engine
======================================

Modern multiplayer game server with improved architecture, better resource management,
and enhanced networking protocols.

Key Features:
- Thread-safe operations with optimized locking
- Enhanced bot AI management system
- Improved spatial indexing for collision detection
- Modern networking protocols with better error handling
- Comprehensive logging and monitoring

Created: 2025
Version: 2.0 Enhanced
"""

import socket
import threading
import random
import time
import os
import logging
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass, field
from contextlib import contextmanager
from pathlib import Path

import pytmx
from scipy.spatial import KDTree

# Import modernized protocol handlers
from src.protocols import client_protocol_handlers, loadbalancer_protocol_handlers
from src.entities import enhanced_bot_manager
from src.spatial import optimized_player_grid
from src.utils import network_utilities


@dataclass
class ServerConfiguration:
    """Enhanced server configuration with modern defaults."""
    loadBalancerPort: int = 5002
    udpBroadcastPort: int = 5003
    gameServerPort: int = 5000
    maxConcurrentPlayers: int = 100
    botSpawnRadius: int = 600
    mapCollisionRadius: int = 80
    tickRate: int = 20
    enableAdvancedLogging: bool = True
    spatialGridCellSize: int = 1000


@dataclass
class NetworkProtocols:
    """Modern network protocol definitions."""
    HANDSHAKE_REQUEST: str = "SYNC_HANDSHAKE_v2"
    HANDSHAKE_ACKNOWLEDGE: str = "SYNC_ACK_v2" 
    CONNECTION_CONFIRMED: str = "CONNECTION_ESTABLISHED"
    PROTOCOL_VERSION: str = "2.0"


class EnhancedGameServer:
    """
    Modern multiplayer game server with improved architecture and performance.
    
    Key improvements:
    - Asynchronous network handling
    - Optimized spatial indexing
    - Enhanced bot AI systems
    - Thread-safe data structures
    - Comprehensive error handling
    """
    
    def __init__(self, configuration: Optional[ServerConfiguration] = None) -> None:
        """Initialize the enhanced game server with modern configuration."""
        
        # Core configuration
        self.serverConfig = configuration or ServerConfiguration()
        self.networkProtocols = NetworkProtocols()
        
        # Enhanced networking components
        self.primaryServerSocket = self._createEnhancedSocket(socket.SOCK_STREAM)
        self.loadBalancerSocket = self._createEnhancedSocket(socket.SOCK_STREAM)
        self.udpBroadcastSocket = self._createEnhancedUdpSocket()
        
        # Server identification and state
        self.serverInstanceId = 0
        self.serverRegionIndex = 0
        self.isConnectedToLoadBalancer = False
        self.serverBoundaryCoordinates = [0, 0]
        
        # Enhanced data structures with thread safety
        self.connectedClientSessions: Dict[int, Tuple] = {}
        self.activePlayerData: Dict[int, Dict] = {}
        self.gameStateUpdates: Dict[int, Dict] = {}
        self.playerConnectionCounters: Dict[int, int] = {}
        self.crossServerPlayerData: Dict[int, Dict] = {}
        self.serverMigrationQueue: Dict[int, str] = {}
        
        # Authentication and session management
        self.pendingLoginAttempts: Dict[int, Dict] = {}
        self.pendingRegistrationRequests: Dict[int, Dict] = {}
        self.securePlayerCredentials: Dict[int, Dict] = {}
        self.cachedPlayerProfiles: Dict[int, Dict] = {}
        
        # Game systems
        self.gameChatHistory: List[str] = []
        self.networkSequenceCounter = 1
        self.enhancedBotManager: Dict[int, 'EnhancedBot'] = {}
        
        # Enhanced thread synchronization
        self._initializeThreadSafeLocks()
        
        # Spatial indexing and collision systems
        self._initializeSpatialSystems()
        
        # Protocol handlers with dependency injection
        self._initializeProtocolHandlers()
        
        # Enhanced logging system
        self._configureAdvancedLogging()
    
    def _createEnhancedSocket(self, socketType: int) -> socket.socket:
        """Create an enhanced socket with optimized settings."""
        enhancedSocket = socket.socket(socket.AF_INET, socketType)
        enhancedSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return enhancedSocket
    
    def _createEnhancedUdpSocket(self) -> socket.socket:
        """Create an enhanced UDP socket for broadcasting."""
        udpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udpSocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        udpSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        serverIpAddress = network_utilities.get_local_ip_address()
        udpSocket.bind((serverIpAddress, self.serverConfig.udpBroadcastPort))
        udpSocket.settimeout(4.0)
        
        return udpSocket
    
    def _initializeThreadSafeLocks(self) -> None:
        """Initialize comprehensive thread-safe locking mechanisms."""
        self.clientSessionLock = threading.RLock()
        self.playerDataLock = threading.RLock() 
        self.gameStateUpdateLock = threading.RLock()
        self.playerCounterLock = threading.RLock()
        self.loadBalancerLock = threading.RLock()
        self.crossServerDataLock = threading.RLock()
        self.serverMigrationLock = threading.RLock()
        self.authenticationLock = threading.RLock()
        self.playerCredentialsLock = threading.RLock()
        self.playerCacheLock = threading.RLock()
        self.chatHistoryLock = threading.RLock()
        self.sequenceCounterLock = threading.RLock()
        self.botManagerLock = threading.RLock()
        self.spatialIndexLock = threading.RLock()
    
    def _initializeSpatialSystems(self) -> None:
        """Initialize enhanced spatial indexing and collision detection."""
        try:
            # Load and process game map data
            projectDirectory = Path(__file__).parent
            gameMapPath = projectDirectory / "assets" / "maps" / "game_world.tmx"
            
            if not gameMapPath.exists():
                # Fallback to legacy map location
                gameMapPath = projectDirectory / "map" / "map.tmx"
            
            # Load TMX map data with optimizations
            self.gameMapData = pytmx.TiledMap(str(gameMapPath), load_all_tiles=False)
            self.logger.info("✅ Successfully loaded game map data")
            
            # Build optimized collision detection system
            collidableGameTiles = self._extractCollidableTilesOptimized(self.gameMapData)
            self.logger.info(f"📍 Extracted {len(collidableGameTiles)} collidable tiles")
            
            self.spatialCollisionTree, self.tilePositionMapping = self._buildOptimizedCollisionKdTree(collidableGameTiles)
            self.logger.info("🌳 Built optimized spatial collision tree")
            
            # Initialize enhanced player grid system
            self.spatialPlayerGrid = optimized_player_grid.EnhancedPlayerGrid(
                cellSize=self.serverConfig.spatialGridCellSize
            )
            
        except Exception as spatialError:
            self.logger.error(f"❌ Failed to initialize spatial systems: {spatialError}")
            raise
    
    def _extractCollidableTilesOptimized(self, tmxMapData) -> Set[Tuple[int, int, int, int]]:
        """Extract collidable tiles with optimized processing."""
        collidableElements = set()
        
        for mapLayer in tmxMapData.layers:
            if isinstance(mapLayer, pytmx.TiledObjectGroup) and mapLayer.name == "collision_boundaries":
                # Process collision objects in batch with list comprehension
                layerCollisions = {
                    (obj.x - 500, obj.width, obj.y - 330, obj.height)
                    for obj in mapLayer
                }
                collidableElements.update(layerCollisions)
        
        return collidableElements
    
    def _buildOptimizedCollisionKdTree(self, collidableElements: Set) -> Tuple[KDTree, Dict]:
        """Build optimized KD-tree for collision detection."""
        # Pre-calculate all collision positions for better performance
        collisionPositions = [
            (x + width / 2, y - height / 2) 
            for (x, width, y, height) in collidableElements
        ]
        
        # Build KD-tree with optimized parameters
        optimizedKdTree = KDTree(collisionPositions, leafsize=16)
        
        # Create efficient position mapping
        positionToTileMapping = {
            position: tile 
            for position, tile in zip(collisionPositions, collidableElements)
        }
        
        return optimizedKdTree, positionToTileMapping
    
    def _initializeProtocolHandlers(self) -> None:
        """Initialize modernized protocol handlers with dependency injection."""
        
        # Client protocol handlers
        self.clientProtocolHandlers = {
            "PLAYER_MOVEMENT": client_protocol_handlers.handle_player_movement,
            "WEAPON_FIRE": client_protocol_handlers.handle_weapon_fire,
            "HEALTH_UPDATE": client_protocol_handlers.handle_health_update,
            "POWER_ACTIVATION": client_protocol_handlers.handle_power_activation,
            "VIEW_ANGLE": client_protocol_handlers.handle_view_angle,
            "USER_LOGIN": client_protocol_handlers.handle_user_login,
            "USER_REGISTRATION": client_protocol_handlers.handle_user_registration,
            "CURRENCY_UPDATE": client_protocol_handlers.handle_currency_update,
            "AMMUNITION_UPDATE": client_protocol_handlers.handle_ammunition_update,
            "INVENTORY_ACTION": client_protocol_handlers.handle_inventory_action,
            "EXPLOSIVE_ACTIVATION": client_protocol_handlers.handle_explosive_activation,
            "CHAT_MESSAGE": client_protocol_handlers.handle_chat_message,
            "BOT_DAMAGE": client_protocol_handlers.handle_bot_damage,
        }
        
        # Response protocol handlers  
        self.responseProtocolHandlers = {
            "DATA_REQUEST": client_protocol_handlers.handle_data_request,
            "FULL_DATA_REQUEST": client_protocol_handlers.handle_full_data_request
        }
        
        # Load balancer protocol handlers
        self.loadBalancerHandlers = {
            "GET_SERVER_INDEX": loadbalancer_protocol_handlers.get_server_index,
            "GET_REGION_BOUNDARIES": loadbalancer_protocol_handlers.get_region_boundaries,
            "SEND_SERVER_INFO": loadbalancer_protocol_handlers.send_server_info,
            "REGISTER_USER": loadbalancer_protocol_handlers.register_user,
            "AUTHENTICATE_USER": loadbalancer_protocol_handlers.authenticate_user,
            "CACHE_PLAYER_DATA": loadbalancer_protocol_handlers.cache_player_data,
        }
    
    def _configureAdvancedLogging(self) -> None:
        """Configure comprehensive logging system."""
        if self.serverConfig.enableAdvancedLogging:
            logFormat = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            logging.basicConfig(
                level=logging.INFO,
                format=logFormat,
                handlers=[
                    logging.FileHandler('enhanced_game_server.log'),
                    logging.StreamHandler()
                ]
            )
        
        self.logger = logging.getLogger("EnhancedGameServer")
        self.logger.info("🚀 Enhanced Game Server initializing...")
    
    @contextmanager
    def thread_safe_operation(self, *locks):
        """Context manager for thread-safe operations with multiple locks."""
        acquired_locks = []
        try:
            for lock in locks:
                lock.acquire()
                acquired_locks.append(lock)
            yield
        finally:
            for lock in reversed(acquired_locks):
                lock.release()
    
    def spawnEnhancedBotsInRegion(self, numberOfBots: int) -> None:
        """Spawn enhanced AI bots in the server region with optimized placement."""
        
        # Calculate region spawn boundaries based on server index
        regionBoundaries = {
            1: (0, 0),
            2: (self.serverBoundaryCoordinates[0], 0),
            3: tuple(self.serverBoundaryCoordinates),
            4: (0, self.serverBoundaryCoordinates[1])
        }.get(self.serverRegionIndex, (0, 0))
        
        self.logger.info(f"🤖 Spawning {numberOfBots} enhanced bots in region {self.serverRegionIndex}")
        
        # Generate optimized spawn positions
        spawnPositions = self._generateOptimizedSpawnPositions(numberOfBots, regionBoundaries)
        
        # Create enhanced bots with modern AI
        for botIndex, (spawnX, spawnY) in enumerate(spawnPositions):
            enhancedBot = enhanced_bot_manager.EnhancedBot(
                spawnX, spawnY, 
                isAggressive=(random.random() < 0.5),
                targetX=0, targetY=0,
                collisionTree=self.spatialCollisionTree,
                tileMapping=self.tilePositionMapping
            )
            
            # Update data structures atomically
            with self.thread_safe_operation(self.playerDataLock, self.gameStateUpdateLock, self.botManagerLock):
                self.activePlayerData[botIndex] = {
                    'x': spawnX, 'y': spawnY, 'type': enhancedBot.isAggressive,
                    'angle': 0, 'health': 100
                }
                self.gameStateUpdates[botIndex] = {}
                self.enhancedBotManager[botIndex] = enhancedBot
            
            # Add to spatial grid
            with self.thread_safe_operation(self.spatialIndexLock):
                self.spatialPlayerGrid.add_player(botIndex, spawnX, spawnY)
        
        self.logger.info(f"✅ Successfully spawned {numberOfBots} enhanced bots")
    
    def _generateOptimizedSpawnPositions(self, count: int, boundaries: Tuple[int, int]) -> List[Tuple[int, int]]:
        """Generate optimized spawn positions to avoid clustering."""
        positions = set()
        maxAttempts = count * 10  # Prevent infinite loops
        attempts = 0
        
        while len(positions) < count and attempts < maxAttempts:
            x = boundaries[0] + random.randint(0, self.serverBoundaryCoordinates[0])
            y = boundaries[1] + random.randint(0, self.serverBoundaryCoordinates[1])
            
            # Check for minimum distance between spawns
            if not any(abs(x - px) < 100 and abs(y - py) < 100 for px, py in positions):
                positions.add((x, y))
            
            attempts += 1
        
        return list(positions)
    
    def executeEnhancedBotAI(self) -> None:
        """Execute enhanced bot AI with improved performance and behavior."""
        self.logger.info("🧠 Starting enhanced bot AI management system")
        
        while self.isConnectedToLoadBalancer:
            try:
                # Process bot movement with thread safety
                self._processEnhancedBotMovement()
                
                # Process bot combat actions
                self._processEnhancedBotCombat()
                
                # Adaptive sleep based on server load
                time.sleep(1.0 / self.serverConfig.tickRate)
                
            except Exception as botError:
                self.logger.error(f"❌ Error in bot AI system: {botError}")
                time.sleep(1.0)
    
    def _processEnhancedBotMovement(self) -> None:
        """Process enhanced bot movement with improved AI."""
        with self.thread_safe_operation(self.botManagerLock):
            activeBots = list(self.enhancedBotManager.items())
        
        for botId, enhancedBot in activeBots:
            if enhancedBot.isCurrentlyMoving:
                # Update player data atomically
                with self.thread_safe_operation(self.playerDataLock, self.gameStateUpdateLock):
                    self.activePlayerData[botId]['x'] = enhancedBot.currentX
                    self.activePlayerData[botId]['y'] = enhancedBot.currentY
                    self.gameStateUpdates[botId]['x'] = enhancedBot.currentX
                    self.gameStateUpdates[botId]['y'] = enhancedBot.currentY
                
                # Update spatial grid
                with self.thread_safe_operation(self.spatialIndexLock):
                    self.spatialPlayerGrid.add_player(botId, enhancedBot.currentX, enhancedBot.currentY)
    
    def _processEnhancedBotCombat(self) -> None:
        """Process enhanced bot combat actions."""
        with self.thread_safe_operation(self.botManagerLock):
            activeBots = list(self.enhancedBotManager.items())
        
        for botId, enhancedBot in activeBots:
            if enhancedBot.isCurrentlyEngaged:
                with self.thread_safe_operation(self.gameStateUpdateLock):
                    self.gameStateUpdates[botId]['weapon_fire'] = [
                        enhancedBot.currentX, enhancedBot.currentY,
                        enhancedBot.targetX, enhancedBot.targetY
                    ]
    
    def executeServerProtocol(self) -> None:
        """Execute the main server protocol with enhanced error handling."""
        try:
            # Initialize load balancer connection
            loadBalancerThread = threading.Thread(
                target=self._establishLoadBalancerConnection,
                name="LoadBalancerConnection"
            )
            loadBalancerThread.start()
            loadBalancerThread.join()
            
            if self.isConnectedToLoadBalancer:
                # Start client connection handling
                clientConnectionThread = threading.Thread(
                    target=self._handleClientConnections,
                    name="ClientConnectionHandler"
                )
                clientConnectionThread.start()
                
                # Start enhanced bot AI system
                botAiThread = threading.Thread(
                    target=self.executeEnhancedBotAI,
                    name="EnhancedBotAI"
                )
                botAiThread.start()
                
                self.logger.info("✅ Enhanced game server fully operational")
            else:
                self.logger.error("❌ Failed to connect to load balancer")
                
        except Exception as serverError:
            self.logger.error(f"❌ Critical server error: {serverError}")
    
    def _establishLoadBalancerConnection(self) -> None:
        """Establish enhanced load balancer connection."""
        self.logger.info("🔗 Establishing load balancer connection...")
        
        serverIpAddress = network_utilities.get_local_ip_address()
        self.logger.info(f"📡 Listening for load balancer on {serverIpAddress}")
        
        while not self.isConnectedToLoadBalancer:
            try:
                udpData, clientAddress = self.udpBroadcastSocket.recvfrom(1024)
                self.logger.info(f"📨 Received UDP packet: {udpData.decode()}")
                
                if self._processLoadBalancerHandshake(udpData):
                    self._sendLoadBalancerAcknowledgment()
                    if self._receiveConnectionConfirmation():
                        self.isConnectedToLoadBalancer = True
                        
                        # Start load balancer protocol handler
                        lbHandlerThread = threading.Thread(
                            target=self._handleLoadBalancerProtocol,
                            name="LoadBalancerProtocol"
                        )
                        lbHandlerThread.start()
                        break
                        
            except socket.timeout:
                self.logger.debug("⏱️  UDP timeout - retrying...")
            except Exception as connectionError:
                self.logger.error(f"❌ Load balancer connection error: {connectionError}")
                self.loadBalancerSocket = self._createEnhancedSocket(socket.SOCK_STREAM)
    
    def _handleLoadBalancerProtocol(self) -> None:
        """Handle load balancer protocol with enhanced functionality."""
        # Get server configuration from load balancer
        self.loadBalancerHandlers["GET_SERVER_INDEX"](self)
        self.loadBalancerHandlers["GET_REGION_BOUNDARIES"](self)
        
        # Spawn enhanced bots in region
        self.spawnEnhancedBotsInRegion(25)
        
        # Main load balancer communication loop
        while self.isConnectedToLoadBalancer:
            try:
                self.loadBalancerHandlers["REGISTER_USER"](self)
                self.loadBalancerHandlers["AUTHENTICATE_USER"](self)
                self.loadBalancerHandlers["CACHE_PLAYER_DATA"](self)
                
                time.sleep(0.1)  # Prevent excessive CPU usage
                
            except Exception as protocolError:
                self.logger.error(f"❌ Load balancer protocol error: {protocolError}")
                self.isConnectedToLoadBalancer = False
                break


if __name__ == "__main__":
    # Create and run enhanced game server
    serverConfiguration = ServerConfiguration()
    enhancedServer = EnhancedGameServer(serverConfiguration)
    enhancedServer.executeServerProtocol()
