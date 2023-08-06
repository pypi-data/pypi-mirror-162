pragma solidity ^0.8;
// SPDX-FileCopyrightText: Copyright 2021 Stephen R. Newell
// SPDX-License-Identifier: MIT

/// @title HelloWorld3
///
/// @author Stephen Newell
///
/// @notice A more complex contract to say hello to the world.
///
/// @dev Uses a transaction to set the greeting and a function to return
/// the greeting.
contract HelloWorld3 {
    /// @dev holds the Hello World greeting.
    string public greeting;

    /**
     * @notice Changes the greeting.
     *
     * @dev Update the contract greeting to this new message.
     *
     * @param _greeting new greeting message
     */
    function setGreeting(string memory _greeting) public {
        greeting = _greeting;
    }

    /**
     * @notice Return the greeting.
     *
     * @dev Function returns a string with the current contract greeting.
     *
     * @return greeting contract greeting value
     */
    function getGreeting() public view returns (string memory) {
        return greeting;
    }
}
