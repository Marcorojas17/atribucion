// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

/**
 * @title AttributionRegistry
 * @author Marco Antonio Rojas Valdovinos
 * @notice Registro inmutable de anclajes de Atribución en Ethereum.
 *         Cada anclaje representa el Merkle root de un lote de acciones
 *         de agentes IA, cumpliendo con EU AI Act Art. 12.
 */
contract AttributionRegistry {
    // ─────────────────────────────────────────────────────────
    // STRUCTS
    // ─────────────────────────────────────────────────────────

    struct Anchor {
        bytes32 merkleRoot;
        string metadataCID;      // IPFS CID con metadata del lote
        uint256 timestamp;
        address submitter;
        uint8 version;
    }

    // ─────────────────────────────────────────────────────────
    // STATE
    // ─────────────────────────────────────────────────────────

    Anchor[] public anchors;
    mapping(address => uint256[]) public anchorsBySubmitter;
    mapping(bytes32 => uint256) public anchorIndexByRoot;
    address public owner;
    uint256 public totalAnchors;

    // ─────────────────────────────────────────────────────────
    // EVENTS
    // ─────────────────────────────────────────────────────────

    event AnchorRegistered(
        uint256 indexed anchorId,
        bytes32 indexed merkleRoot,
        address indexed submitter,
        string metadataCID,
        uint256 timestamp
    );

    event OwnerChanged(address indexed previousOwner, address indexed newOwner);

    // ─────────────────────────────────────────────────────────
    // MODIFIERS
    // ─────────────────────────────────────────────────────────

    modifier onlyOwner() {
        require(msg.sender == owner, "AttributionRegistry: not owner");
        _;
    }

    // ─────────────────────────────────────────────────────────
    // CONSTRUCTOR
    // ─────────────────────────────────────────────────────────

    constructor() {
        owner = msg.sender;
        emit OwnerChanged(address(0), msg.sender);
    }

    // ─────────────────────────────────────────────────────────
    // WRITE
    // ─────────────────────────────────────────────────────────

    /**
     * @notice Registra un nuevo anclaje.
     * @param merkleRoot Root de Merkle del lote de acciones.
     * @param metadataCID CID de IPFS con metadata del lote.
     */
    function registerAnchor(
        bytes32 merkleRoot,
        string calldata metadataCID
    ) external returns (uint256) {
        require(merkleRoot != bytes32(0), "AttributionRegistry: empty root");
        require(
            anchorIndexByRoot[merkleRoot] == 0 && anchors.length == 0 
                ? true 
                : anchorIndexByRoot[merkleRoot] == 0,
            "AttributionRegistry: root already registered"
        );

        Anchor memory newAnchor = Anchor({
            merkleRoot: merkleRoot,
            metadataCID: metadataCID,
            timestamp: block.timestamp,
            submitter: msg.sender,
            version: 1
        });

        anchors.push(newAnchor);
        uint256 anchorId = anchors.length - 1;
        anchorsBySubmitter[msg.sender].push(anchorId);
        anchorIndexByRoot[merkleRoot] = anchorId + 1;
        totalAnchors += 1;

        emit AnchorRegistered(
            anchorId,
            merkleRoot,
            msg.sender,
            metadataCID,
            block.timestamp
        );

        return anchorId;
    }

    /**
     * @notice Transfiere ownership del contrato.
     */
    function transferOwnership(address newOwner) external onlyOwner {
        require(newOwner != address(0), "AttributionRegistry: zero address");
        address previous = owner;
        owner = newOwner;
        emit OwnerChanged(previous, newOwner);
    }

    // ─────────────────────────────────────────────────────────
    // READ
    // ─────────────────────────────────────────────────────────

    /**
     * @notice Devuelve un anclaje por ID.
     */
    function getAnchor(uint256 anchorId) external view returns (Anchor memory) {
        require(anchorId < anchors.length, "AttributionRegistry: invalid id");
        return anchors[anchorId];
    }

    /**
     * @notice Devuelve todos los anclajes de un submitter.
     */
    function getAnchorsBySubmitter(address submitter)
        external
        view
        returns (uint256[] memory)
    {
        return anchorsBySubmitter[submitter];
    }

    /**
     * @notice Verifica que un Merkle root está registrado.
     */
    function isRootRegistered(bytes32 merkleRoot) external view returns (bool) {
        return anchorIndexByRoot[merkleRoot] != 0;
    }

    /**
     * @notice Devuelve el total de anclajes.
     */
    function getTotalAnchors() external view returns (uint256) {
        return totalAnchors;
    }
}