from flask import (Blueprint, flash, redirect, render_template)
from trackyr.trackyr_config.forms import ConfigForm

import lib.core.version as versionCheck

trackyr_config = Blueprint('trackyr_config', __name__)

@trackyr_config.route("/trackyr_config/update", methods=['GET', 'POST'])
def update():
    result=versionCheck.is_latest_version()
    if result:
        message="You are up to date."
        flash(message, 'top_flash_success')
    else:
        message="An update is available."
        flash(message, 'top_flash_success')
    return render_template('trackyr-config.html', title='Config')
