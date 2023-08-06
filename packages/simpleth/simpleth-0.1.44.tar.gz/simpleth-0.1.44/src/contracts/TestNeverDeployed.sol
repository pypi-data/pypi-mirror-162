pragma solidity ^0.8;
// SPDX-FileCopyrightText: Copyright 2021 Stephen R. Newell
// SPDX-License-Identifier: MIT

/**
 * @title TestNeverDeployed
 *
 * @author Stephen Newell
 *
 * @notice Used with PyTest test cases that attempt to use a contract
 * without doing a connect().  This contract should never be deployed.
 *
 * @dev For test use, this contract should be compiled but should not
 * have a address file (`.addr`) in the `artifacts` directory.
 */
contract TestNeverDeployed {
    /// @dev state variable to use with a Contract().get_var()
    string public text = "I should never get deployed";

     /**
     * @notice Update contract text variable
     *
     * @dev Should never be called since contract does not deploy.
     *
     * @param _text becomes the contract text value.
     */
    function setText(string memory _text) public {
        text = _text;
    }
}