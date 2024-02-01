# Github Webpage Scraper
This project is a simple web scraper that uses Jekyll to serve a Github Page locally.

## Installation
### Install Jekyll
YOu can follow this [link](https://jekyllrb.com/docs/installation/) to install Jekyll on any platform.

On Ubuntu, simply run the following commands:
```bash
sudo apt-get install ruby-full build-essential zlib1g-dev 
```
And add this to your `~/.bashrc` or `~/.zshrc`:
```bash
# JEKILL Installation
# Install Ruby Gems to ~/gems
export GEM_HOME="$HOME/gems"
export PATH="$HOME/gems/bin:$PATH"
```
Then run:
```bash
source ~/.bashrc
gem install jekyll bundler
```

## Runninng the project
### Serving a Github Page locally with Jekyll
To serve a Github Page locally, you need to have Jekyll installed. Then, you can run the following command:
```bash
cd <repository>
bundle install
bundle exec jekyll serve
```
Then, you can access the page at `http://localhost:4000` in your browser.