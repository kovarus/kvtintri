# Tintri Automation Library

This is a helper library used to manage Tintri VMstore devices via python. Use this for generating reports and automating actions on large numbers of virtual machines.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisities

This library uses the requests and prettytable libraries.

```
pip install requests
pip install prettytable
```

### Installing

Once the requests and prettytable modules are installed, kvtintri can be installed with pip.

```
python setup.py install
```

Once installed, you can test it with the following code (replacing the credentials where necessary). This will return a dictionary of virtual machines.

```
import kvtintri
session = kvtintri.VMStore.login(device="10.25.36.10", username="admin", password="secret!")
session.get_vms(from_name="my_vm_name")
```

## Built With

* Atom

## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/your/project/tags).

## Authors

* **Russell Pope** - [russellpope](https://github.com/russellpope)

## License

This project is licensed under the Apache 2.0 License - see the [LICENSE.txt](LICENSE.txt) file for details
