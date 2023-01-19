# BodyApp in Kivy framework

This is a rudimentary mobile application, written in Kivy framework (Python), targetting Android (see `buildozer.spec`). The application takes user's
body height and weight as input and estimates his/her body measurements and visualizes the corresponding SMPL mesh.

## Development setup

### Step 1 

Clone this repository in desired location, such as `/home/<user>/kivy-body-app/` by running:
  
  ```
  git clone https://github.com/kristijanbartol/kivy-body-app.git
  ```
  
  in `/home/<user>/` folder.
  
### Step 2

Install buildozer in a separate folder, for example `/home/<user>/buildozer by running:

```
git clone https://github.com/kivy/buildozer.git
cd buildozer
sudo python setup.py install
```

in `/home/<user>/` folder.

### Step 3

Install buildozer's dependencies:

```
sudo apt update
sudo apt install -y git zip unzip openjdk-17-jdk python3-pip autoconf libtool pkg-config zlib1g-dev libncurses5-dev libncursesw5-dev libtinfo5 cmake libffi-dev libssl-dev
pip3 install --user --upgrade Cython==0.29.19 virtualenv  # the --user should be removed if you do this in a venv

# add the following line at the end of your ~/.bashrc file
export PATH=$PATH:~/.local/bin/
```

### Step 4

Now you can build and run the app on your phone based on the provided `buildozer.spec` file by running:

```
buildozer android debug deploy run
```

in the `/home/<user>/kivy-body-app/` folder.

## Troubleshooting

Various errors can happen on the way. Before going any further, check whether the following, working setup is specified correctly in the
`buildozer.spec`:

- armeabi-v7a
- android.minapi = 21
- android.api = 29

If the error is either `INSTALL_FAILED_VERSION_DOWNGRADE` or `INSUFFICIENT_MEMORY_ERROR`, try deleting the app from device and rerunning.

### (!) Do not try (!)

Trying to make it work with PyTorch - continue using NumPy instead.

## License

Software Copyright License for **non-commercial scientific research purposes**.
Please read carefully the [terms and conditions](https://github.com/vchoutas/smplx/blob/master/LICENSE) and any accompanying documentation before you download and/or use the SMPL-X/SMPLify-X model, data and software, (the "Model & Software"), including 3D meshes, blend weights, blend shapes, textures, software, scripts, and animations. By downloading and/or using the Model & Software (including downloading, cloning, installing, and any other use of this github repository), you acknowledge that you have read these terms and conditions, understand them, and agree to be bound by them. If you do not agree with these terms and conditions, you must not download and/or use the Model & Software. Any infringement of the terms of this agreement will automatically terminate your rights under this [License](./LICENSE).

