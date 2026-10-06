// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

/**
 * @title KAFRegistry
 * @notice Registro público e inmutable de certificados KAF.
 *         Cualquiera puede verificar sin permiso ni autenticación.
 * @author Marco Antonio Rojas Valdovinos
 */
contract KAFRegistry {
    // ─── STRUCTS ───────────────────────────────────────────────

    struct KAFRecord {
        string certificateId;
        string agentId;
        string agentDid;
        string level;
        uint256 issuedAt;
        uint256 expiresAt;
        bytes32 assessmentHash;
        address issuer;
        bool revoked;
    }

    // ─── STATE ─────────────────────────────────────────────────

    KAFRecord[] public records;
    mapping(string => uint256) public indexByCertId;
    mapping(string => bool) public isValidCertId;
    address public owner;
    mapping(address => bool) public authorizedIssuers;
    uint256 public totalIssued;
    uint256 public totalRevoked;

    // ─── EVENTS ────────────────────────────────────────────────

    event CertificateIssued(
        uint256 indexed recordId,
        string certificateId,
        string agentId,
        string level,
        address indexed issuer
    );
    event CertificateRevoked(
        string certificateId,
        address indexed revokedBy,
        uint256 revokedAt
    );
    event IssuerAuthorized(address indexed issuer);
    event IssuerRevoked(address indexed issuer);
    event OwnershipTransferred(address indexed from, address indexed to);

    // ─── MODIFIERS ─────────────────────────────────────────────

    modifier onlyOwner() {
        require(msg.sender == owner, "not owner");
        _;
    }

    modifier onlyAuthorized() {
        require(
            authorizedIssuers[msg.sender] || msg.sender == owner,
            "not authorized"
        );
        _;
    }

    // ─── CONSTRUCTOR ───────────────────────────────────────────

    constructor() {
        owner = msg.sender;
        authorizedIssuers[msg.sender] = true;
        emit IssuerAuthorized(msg.sender);
    }

    // ─── ADMIN ─────────────────────────────────────────────────

    function authorizeIssuer(address issuer) external onlyOwner {
        require(issuer != address(0), "zero address");
        authorizedIssuers[issuer] = true;
        emit IssuerAuthorized(issuer);
    }

    function revokeIssuer(address issuer) external onlyOwner {
        authorizedIssuers[issuer] = false;
        emit IssuerRevoked(issuer);
    }

    function transferOwnership(address newOwner) external onlyOwner {
        require(newOwner != address(0), "zero address");
        address previous = owner;
        owner = newOwner;
        emit OwnershipTransferred(previous, newOwner);
    }

    // ─── ISSUE ─────────────────────────────────────────────────

    function issueCertificate(
        string calldata certificateId,
        string calldata agentId,
        string calldata agentDid,
        string calldata level,
        uint256 validityDays,
        bytes32 assessmentHash
    ) external onlyAuthorized returns (uint256) {
        require(!isValidCertId[certificateId], "cert already exists");
        require(validityDays > 0, "validity must be > 0");
        require(
            _isValidLevel(level),
            "invalid level (KAF-1|KAF-2|KAF-3|KAF-4)"
        );

        uint256 expiresAt = block.timestamp + (validityDays * 1 days);

        KAFRecord memory newRecord = KAFRecord({
            certificateId: certificateId,
            agentId: agentId,
            agentDid: agentDid,
            level: level,
            issuedAt: block.timestamp,
            expiresAt: expiresAt,
            assessmentHash: assessmentHash,
            issuer: msg.sender,
            revoked: false
        });

        records.push(newRecord);
        uint256 recordId = records.length - 1;
        indexByCertId[certificateId] = recordId;
        isValidCertId[certificateId] = true;
        totalIssued += 1;

        emit CertificateIssued(recordId, certificateId, agentId, level, msg.sender);

        return recordId;
    }

    function revokeCertificate(string calldata certificateId)
        external
        onlyAuthorized
    {
        require(isValidCertId[certificateId], "cert not found");
        uint256 idx = indexByCertId[certificateId];
        require(!records[idx].revoked, "already revoked");

        records[idx].revoked = true;
        totalRevoked += 1;

        emit CertificateRevoked(certificateId, msg.sender, block.timestamp);
    }

    // ─── VIEW ──────────────────────────────────────────────────

    function verify(string calldata certificateId)
        external
        view
        returns (bool valid, KAFRecord memory record)
    {
        if (!isValidCertId[certificateId]) {
            return (
                false,
                KAFRecord("", "", "", "", 0, 0, bytes32(0), address(0), false)
            );
        }
        record = records[indexByCertId[certificateId]];
        valid = !record.revoked && record.expiresAt > block.timestamp;
    }

    function totalRecords() external view returns (uint256) {
        return records.length;
    }

    // ─── INTERNAL ──────────────────────────────────────────────

    function _isValidLevel(string memory level) private pure returns (bool) {
        bytes32 h = keccak256(bytes(level));
        return (
            h == keccak256(bytes("KAF-1")) ||
            h == keccak256(bytes("KAF-2")) ||
            h == keccak256(bytes("KAF-3")) ||
            h == keccak256(bytes("KAF-4"))
        );
    }
}