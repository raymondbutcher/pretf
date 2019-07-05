[direnv](https://direnv.net/) is a tool for setting up development environments on a per-directory basis. 

[asdf-vm](https://asdf-vm.com/) is a tool for installing and managing software versions.

These tools work great with Pretf projects. This example `.envrc` file does the following when you `cd` into the project directory:

* Creates and activates a virtual environment for Python.
* Ensures that Pretf is installed.
* Ensures that Terraform is installed.
* Adds a `terraform` shim to run Pretf instead of Terraform.

```shell
# Use a virtual environment for Python.
layout python3

# Install Python packages.
python_packages="
pretf[aws]
"
for package in $python_packages; do
  pip install $package | grep -v "Requirement already satisfied:" || true
done

# Install asdf-vm plugins and tools.
asdf_tools="
terraform 0.12.3
"
if command -v asdf > /dev/null; then
  echo "${asdf_tools}" > .tool-versions
  for plugin in $(cut -d ' ' -f 1 .tool-versions); do
      if ! asdf plugin-list | grep $plugin > /dev/null; then
          echo "Installing asdf plugin $plugin"
          asdf plugin-add $plugin
      fi
  done
  asdf install
fi

# Add a terraform shim to run Pretf instead of Terraform.
PATH_add "$(mkdir -p .direnv/bin && cd $_ && ln -fs $(which pretf) terraform && pwd)"
```
