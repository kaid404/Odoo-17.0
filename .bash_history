git clone https://www.github.com/odoo/odoo --depth 1 --branch 17.0 /opt/odoo17.0/odoo
cd /opt/odoo17.0
python3 -m venv odoo-venv
source odoo-venv/bin/activate
pip3 install wheel
pip3 install -r odoo/requirements.txt
deactivate
mkdir /opt/odoo17.0/odoo-custom-addons
exit
