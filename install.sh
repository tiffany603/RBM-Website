#!/bin/bash
echo "Creating virtual env folder in venv..." 
virtualenv venv
echo "Activating the virtual env..."
source venv/bin/activate
echo "Installing all requirements..."
pip install -r requirements.txt
echo "Linking post commit and merge hooks..."
cd .git/hooks
ln -s ../../hooks/pre-commit pre-commit
ln -s ../../hooks/post-merge post-merge
cd ../../
echo "Cloning rbm lib.."
git clone https://github.com/fleurette/RBM.git rbm_website/libs/rbm_lib

echo "Setting up database.."
rm database.sqlite3
python manage.py syncdb --noinput

echo "Finished, activate the virtual env with ./activate or 'source venv/bin/activate' or 'source venv/bin/activate.csh'"
