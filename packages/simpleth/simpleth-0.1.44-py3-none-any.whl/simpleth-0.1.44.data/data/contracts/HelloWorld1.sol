pragma solidity ^0.8;
// SPDX-FileCopyrightText: Copyright 2021 Stephen R. Newell
// SPDX-License-Identifier: MIT

/// @title HelloWorld1
///
/// @author Stephen Newell
///
/// @notice The simplest contract to say hello to the world.
///
/// @dev Uses a public state variable to hold the greeting
contract HelloWorld1 {
    /// @dev Hello World greeting.
    string public greeting = "Hello World!";
}
