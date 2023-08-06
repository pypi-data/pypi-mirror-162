pragma solidity ^0.8;
// SPDX-FileCopyrightText: Copyright 2021 Stephen R. Newell
// SPDX-License-Identifier: MIT

/// @title HelloWorld2
///
/// @author Stephen Newell
///
/// @notice A slightly more involved contract to say hello to the world.
///
/// @dev Uses a function to return the greeting.
contract HelloWorld2 {

    /**
     * @notice Return the Hello World greeting.
     *
     * @dev Function returns a string with the greeting defined
     * in the function.
     */
    function getGreeting() public pure returns (string memory) {
        return 'Hello World!';
    }
}
