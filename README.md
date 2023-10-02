# Product Creation Request Module for Odoo

## Description
The "Product Creation Request" module is a custom extension for Odoo that allows users to request the creation of new products within the system.

## Features
- Users can submit product creation requests.
- Requested products go through an approval workflow.
- Administrators can review and approve product creation requests.
- Once approved, new products are created in the system.

## Installation
To install this module in your Odoo instance, follow these steps:

1. Clone this repository into the `addons` directory of your Odoo instance:
```
cd custom_addons
git pull origin https://github.com/veone/creation_request.git

```

2. Restart your Odoo instance.

3. Log in to the Odoo admin interface.

4. Navigate to "Apps" and search for "Product Creation Request."

5. Click "Install."

## Configuration
- Configure approval workflows and permissions as needed in the Odoo settings.
- Set up notification preferences for product creation requests.

## Usage
1. Log in as a user with the necessary permissions.
2. Navigate to the "Product Creation Request" menu.
3. Click "Create Request" and fill out the required information.
4. Submit the request.
5. Administrators will receive notifications and can review/approve the request.

## Contributors
- Veone (@veone)

## License
This module is distributed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Support
For any questions, suggestions, or bug reports, please open an issue on this repository.

## Changelog
- **16.0.1 (2023-10-01)**: Initial release.

