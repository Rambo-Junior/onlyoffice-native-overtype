/* OO_OVERTYPE_UNDO_RC3: post-FinalizeAction grouping, ONLYOFFICE 9.4.0-129.
 * Unlike RC2 this does not depend on a later call to CheckUnionLastPoints.
 * SPDX-License-Identifier: AGPL-3.0-only
 */
(function() {
    "use strict";
    // The preexisting RC2 hook executes while the current action is still open.
    // A point selected here may later be finalized or removed. Store intent on
    // the document and find the actual committed point only AFTER FinalizeAction.
    CDocument.prototype._ooMarkOvertypeUndoPoint = function() {
        var serial = (this._ooOvertypeUndoSerial || 0) + 1;
        this._ooOvertypeUndoSerial = serial;
        var history = this.History;
        this._ooOvertypePendingRC3 = {
            epoch: this._ooOvertypeUndoEpoch || 0,
            serial: serial,
            at: Date.now(),
            point: history && history.Points && history.Points[history.Index]
        };
    };

    CDocument.prototype._ooFinishOvertypeUndoRC3 = function() {
        var next = this._ooOvertypePendingRC3;
        this._ooOvertypePendingRC3 = null;
        if (!next || this.IsActionStarted()) return false;
        var h = this.History;
        if (!h || !h.Points || h.Index !== h.Points.length - 1 || h.Index < 0 ||
            h.UndoRedoInProgress || !h.Is_On || !h.Is_On()) return false;
        var points = h.Points, right = points[h.Index];
        // In particular, reject actions which generated a different final point.
        if (!right || right !== next.point || !right.Additional || !right.Items ||
            right.Items.length < 2 ||
            right.Description !== AscDFH.historydescription_Document_AddLetter ||
            (right.Items[0].Data && right.Items[0].Data.Type === AscDFH.historyitem_TableId_Description))
            return false;
        var rightMeta = {epoch: next.epoch, count:1,
                         lastSerial:next.serial, lastTime:next.at};
        right.Additional.ooOvertypeRC3 = rightMeta;
        // First character in a run needs no union, but the metadata must survive.
        if (h.Index < 1) return true;
        var left = points[h.Index - 1], a = left && left.Additional && left.Additional.ooOvertypeRC3;
        if (!a || a.epoch !== rightMeta.epoch || a.lastSerial + 1 !== next.serial ||
            a.count < 1 || a.count >= 32 || next.at < a.lastTime ||
            next.at - a.lastTime > 1800 ||
            left.Description !== AscDFH.historydescription_Document_AddLetter ||
            !left.Items || left.Items.length < 2 ||
            left.Additional.FormFilling !== right.Additional.FormFilling ||
            (left.Items[0].Data && left.Items[0].Data.Type === AscDFH.historyitem_TableId_Description))
            return true;
        var border = points.length - 2;
        // Never cross either a normal-save or a user-save boundary.
        if ((h.SavedIndex !== null && h.SavedIndex !== undefined && h.SavedIndex >= border) ||
            (h.UserSavedIndex !== null && h.UserSavedIndex !== undefined && h.UserSavedIndex >= border))
            return true;
        var additional = {ooOvertypeRC3: {
            epoch:a.epoch, count:a.count+1, lastSerial:next.serial, lastTime:next.at
        }};
        if (left.Additional.FormFilling) additional.FormFilling = left.Additional.FormFilling;
        var merged = {State:left.State, Items:left.Items.concat(right.Items),
                      Time:left.Time, Additional:additional, Description:left.Description};
        points.splice(border, 2, merged);
        if (h.Index >= points.length) {
            var delta = -h.Index + (points.length - 1);
            h.Index += delta;
            h.RecIndex = Math.max(-1, h.RecIndex + delta);
        }
        return true;
    };
})();
