# Ghoul

A command line interface for your GitHub repositories.

**WARNING!** This project is at a very early stage, definitely not for the
faint of heart! However, if you like breaking stuff and reporting bugs, feel
free to give Ghoul a try.

## Why?

GitHub's user interface is nice. It's straightforward, easy to use and gets the
job done. But having to use a web UI when most of your coding/versioning
happens in text editors and command lines is sometimes... annoying.

The idea behind Ghoul is having a human-friendly tool that helps you manage
your GitHub comments, issues, pull requests, etc., from the warmth and
practicality of your terminal.

For that purpose, the parameters mostly try to mimic the ones in Git commands,
so if you know Git you already know Ghoul.

## Installation

```bash
# Clone this repo
git clone https://github.com/YagoGG/ghoul.git
cd ghoul
# Install the dependencies
pip install -r requirements.txt
# Create a symlink to use Ghoul anywhere
sudo ln -s $(pwd)/ghoul.py /usr/bin/gh
```

Ghoul will be uploaded to the [Python Package Index](https://pypi.python.org/),
so the installation process is going to be much easier real soon.

## Usage

Try running `gh -h` for details on how to use it.

## Contributing

Do you miss anything? Something isn't working as expected? Scared of
[monsters](https://en.wikipedia.org/wiki/Ghoul)? File an issue or, even better,
a pull request!

In the (rather likely) case you find something strange, please see if there's
any [open issue](https://github.com/YagoGG/ghoul/issues) for that problem
before filing a new one.

Right now there isn't any mailing list or similar, so feel free to create an
issue for any questions you may have.

## License

Ghoul's code is under the MIT license, which can be read in this repo's
[LICENSE](./LICENSE) file.

---

&copy; 2017 [Yago González](https://github.com/YagoGG). All rights reserved.
