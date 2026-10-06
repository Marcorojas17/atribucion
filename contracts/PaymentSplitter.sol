// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

/**
 * @title PaymentSplitter
 * @notice Distribuye pagos entre múltiples beneficiarios.
 *         Usado para repartir ingresos de Atribución entre
 *         fundador, infraestructura, desarrollo y reserva PQC.
 * @author Marco Antonio Rojas Valdovinos
 */
contract PaymentSplitter {
    // ─── STATE ─────────────────────────────────────────────────

    address[] public payees;
    uint256[] public shares;
    uint256 public totalShares;
    uint256 public totalReleased;

    mapping(address => uint256) public released;
    mapping(address => uint256) public indexByAddress;

    // ─── EVENTS ────────────────────────────────────────────────

    event PayeeAdded(address indexed account, uint256 shares);
    event PaymentReleased(address indexed to, uint256 amount);
    event PaymentReceived(address indexed from, uint256 amount);
    event PayeeRemoved(address indexed account);

    // ─── MODIFIERS ─────────────────────────────────────────────

    modifier onlyPayee() {
        require(indexByAddress[msg.sender] > 0, "not payee");
        _;
    }

    // ─── CONSTRUCTOR ───────────────────────────────────────────

    constructor(address[] memory _payees, uint256[] memory _shares) {
        require(_payees.length == _shares.length, "length mismatch");
        require(_payees.length > 0, "no payees");

        for (uint256 i = 0; i < _payees.length; i++) {
            _addPayee(_payees[i], _shares[i]);
        }
    }

    // ─── RECEIVE ───────────────────────────────────────────────

    receive() external payable {
        emit PaymentReceived(msg.sender, msg.value);
    }

    // ─── INTERNAL ──────────────────────────────────────────────

    function _addPayee(address account, uint256 shares_) private {
        require(account != address(0), "zero address");
        require(shares_ > 0, "zero shares");
        require(indexByAddress[account] == 0, "already added");

        payees.push(account);
        shares.push(shares_);
        indexByAddress[account] = payees.length;
        totalShares += shares_;

        emit PayeeAdded(account, shares_);
    }

    // ─── EXTERNAL ──────────────────────────────────────────────

    /**
     * @notice Libera el pago correspondiente a una cuenta.
     */
    function release(address payable account) external {
        uint256 index = indexByAddress[account];
        require(index > 0, "not payee");

        uint256 totalReceived = address(this).balance + totalReleased;
        uint256 payment = (totalReceived * shares[index - 1]) /
            totalShares - released[account];

        require(payment != 0, "nothing to release");

        released[account] += payment;
        totalReleased += payment;

        (bool success, ) = account.call{value: payment}("");
        require(success, "transfer failed");

        emit PaymentReleased(account, payment);
    }

    /**
     * @notice Libera el pago a todos los beneficiarios.
     */
    function releaseAll() external {
        for (uint256 i = 0; i < payees.length; i++) {
            address payable payee = payable(payees[i]);
            uint256 totalReceived = address(this).balance + totalReleased;
            uint256 payment = (totalReceived * shares[i]) /
                totalShares - released[payee];

            if (payment > 0) {
                released[payee] += payment;
                totalReleased += payment;
                (bool success, ) = payee.call{value: payment}("");
                require(success, "transfer failed");
                emit PaymentReleased(payee, payment);
            }
        }
    }

    // ─── VIEW ──────────────────────────────────────────────────

    function getPayees() external view returns (address[] memory) {
        return payees;
    }

    function getShares() external view returns (uint256[] memory) {
        return shares;
    }

    function getBalance() external view returns (uint256) {
        return address(this).balance;
    }

    function pendingPayment(address account) external view returns (uint256) {
        uint256 index = indexByAddress[account];
        if (index == 0) return 0;

        uint256 totalReceived = address(this).balance + totalReleased;
        return (totalReceived * shares[index - 1]) / totalShares - released[account];
    }
}