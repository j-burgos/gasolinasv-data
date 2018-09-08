#!/usr/bin/env bash
# https://gist.github.com/ziadoz/3e8ab7e944d02fe872c3454d17af31a5

OS="$(uname -s)"

function linux_setup() {
  # Remove and install chrome
  echo "Installing Chrome..."
  sudo apt-get remove google-chrome-stable
  sudo curl -sS -o - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add
  sudo echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list
  sudo apt-get -y update
  sudo apt-get -y install unzip google-chrome-stable

  # Install chromedriver
  CHROME_DRIVER_VERSION=`curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE`
  echo "Installing local chromedriver:$CHROME_DRIVER_VERSION"
  curl http://chromedriver.storage.googleapis.com/$CHROME_DRIVER_VERSION/chromedriver_linux64.zip \
    -o ./selenium/chromedriver_linux64.zip \
    -s
  pushd selenium
  unzip chromedriver_linux64.zip -d ./
  rm chromedriver_linux64.zip
  popd

  # Installing python dependencies
  echo "Installing python packages"
  pip install -r requirements.txt
}

if [ "$(expr substr ${OS} 1 5)" == "Linux" ]; then
    linux_setup
else
  echo "OS: ${OS} not supported"
  exit 1
fi

