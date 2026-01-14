from odoo import models, fields, _
from odoo.exceptions import UserError

from ..models import media_unit


class ReturnMedia(models.TransientModel):
    """ Retrun Media Wizard """
    _name = "return.media"
    _description = "Media Author"

    media_id = fields.Many2one('op.media', 'Media', readonly=True)
    media_unit_id = fields.Many2one(
        'op.media.unit', 'Media Unit', readonly=True, required=True)
    actual_return_date = fields.Date(
        'Actual Return Date', default=lambda self: fields.Date.today(),
        required=True)

    def do_return(self):
        for media in self:
            if media.media_unit_id.state and \
                    media.media_unit_id.state == 'issue':
                media_move_search = self.env['op.media.movement'].search(
                    [('media_unit_id', '=', media.media_unit_id.id),
                     ('state', '=', 'issue')])
                if not media_move_search:
                    raise UserError(_("Can't return media."))
                media_move_search.return_media(media.actual_return_date)
            else:
                raise UserError(_("Media Unit can not be returned \
                because it's state is : %s") % (dict(
                    media_unit.unit_states).get(
                    media.media_unit_id.state)))
