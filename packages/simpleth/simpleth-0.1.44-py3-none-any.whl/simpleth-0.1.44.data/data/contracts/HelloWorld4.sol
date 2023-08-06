pragma solidity ^0.8;
// SPDX-FileCopyrightText: Copyright 2021 Stephen R. Newell
// SPDX-License-Identifier: MIT

/**
 * @title HelloWorld4
 *
 * @author Stephen Newell
 *
 * @notice Adds an event to the constructor.
 *
 * @dev Find the greeting in the emitted event.
 */
contract HelloWorld4 {
    /// @dev the greeting to display
    string public greeting;

    /**
     * @notice Emitted when contract is constructed
     *
     * @param timestamp block time when constructed
     * @param sender address sending the constructor
     * @param initGreeting constructor arg with a greeting
     * @param HelloWorld4 address of the newly deployed contract
     */
    event HelloWorld4Constructed(
        uint timestamp,
        address sender,
        string initGreeting,
        address HelloWorld4
    );

    /**
     * @notice Create a new HelloWorld4 contract on the blockchain.
     *
     * @dev Emits HelloWord4().
     *
     * @param _initGreeting set as the greeting string
     */
    constructor(string memory _initGreeting) {
        greeting = _initGreeting;
        emit HelloWorld4Constructed(
            block.timestamp,
            msg.sender,
            greeting,
            address(this)
        );
    }
}
