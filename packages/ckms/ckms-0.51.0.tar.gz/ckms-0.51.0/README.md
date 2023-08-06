# Crypto Key Management Framework


## Requirements

### Yubikey provider

- SWIG


## Notes

- On Apple Mac M1 processors, the YubIHSM may have issues detecting the
  USB library. Point the `usb` library to the proper location by setting
  an environment variable:

  `export DYLD_LIBRARY_PATH=/opt/homebrew/lib`

  (or the proper path on your system).
