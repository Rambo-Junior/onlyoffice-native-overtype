/* OO_OVERTYPE_UNDO_RC4 -- ONLYOFFICE Overtype Native Undo RC4 -- SDKJS 9.4.0-129 only.
 * Targeted change: preserve upstream handling of historyitem_TableId_Description
 * during grouping and report precise fail-closed reasons to an optional localhost
 * diagnostics collector (NO document text is sent). SPDX-License-Identifier: AGPL-3.0-only
 */
(function () {
    "use strict";
    function trace(doc, phase, why, h, p) {
        // Completely optional. Only metadata; NEVER send typed text, file paths or document IDs.
        try {
            if (typeof WebSocket !== 'function') return;
            var message = JSON.stringify({phase:phase,why:why,
                index:h && h.Index, length:h && h.Points && h.Points.length,
                count:p && p.Items && p.Items.length,
                description:p && p.Description,
                firstType:p && p.Items && p.Items[0] && p.Items[0].Data && p.Items[0].Data.Type,
                epoch:doc._ooOvertypeUndoEpoch || 0,
                serial:doc._ooOvertypeUndoSerial || 0});
            var ws = new WebSocket('ws://127.0.0.1:39169/');
            ws.onopen = function () {try {ws.send(message);ws.close();}catch(_e){}};
            ws.onerror = function () {};
        } catch (_ignore) {}
    }
    function isTableDescription(item) {
        return !!(item && item.Data && item.Data.Type === AscDFH.historyitem_TableId_Description);
    }
    function isLetterDescription(desc) {
        return desc === AscDFH.historydescription_Document_AddLetter ||
               desc === AscDFH.historydescription_Document_AddLetterUnion;
    }
    CDocument.prototype._ooMarkOvertypeUndoPoint = function () {
        var h = this.History;
        var serial = (this._ooOvertypeUndoSerial || 0) + 1;
        this._ooOvertypeUndoSerial = serial;
        this._ooOvertypePendingRC3 = {
            epoch:this._ooOvertypeUndoEpoch || 0,
            serial:serial, at:Date.now(),
            point:h && h.Points && h.Points[h.Index]
        };
        trace(this,'mark','accepted',h,this._ooOvertypePendingRC3.point);
    };
    CDocument.prototype._ooFinishOvertypeUndoRC3 = function () {
        var pending = this._ooOvertypePendingRC3;
        this._ooOvertypePendingRC3 = null;
        if (!pending) return false;
        var h = this.History;
        var p = h && h.Points;
        function no(reason) { trace(thisDoc,'reject',reason,h,p && p[h.Index]);return false; }
        var thisDoc = this;
        if (this.IsActionStarted()) return no('still-active-action');
        if (!h || !p || h.Index !== p.length - 1 || h.Index < 0 || h.UndoRedoInProgress ||
            !h.Is_On || !h.Is_On()) return no('bad-history-index-or-state');
        var right = p[h.Index];
        if (!right || !right.Additional || !right.Items || right !== pending.point)
            return no('point-replaced-or-missing');
        if (right.Items.length < 2) return no('right-too-few-items');
        if (!isLetterDescription(right.Description)) return no('right-description');
        // A TableId_Description as the FIRST history item is normal in upstream
        // CheckUnionLastPoints (which strips it on union). RC3 incorrectly rejected it.
        var meta = {epoch:pending.epoch,count:1,lastSerial:pending.serial,lastTime:pending.at};
        right.Additional.ooOvertypeRC3 = meta;
        trace(this,'tag','final-history-point',h,right);
        if (h.Index < 1) return true;
        var left = p[h.Index - 1], a = left && left.Additional && left.Additional.ooOvertypeRC3;
        if (!a) { trace(this,'boundary','previous-point-is-not-overwrite',h,left);return true; }
        if (a.epoch !== meta.epoch || a.lastSerial + 1 !== pending.serial ||
            a.count < 1 || a.count >= 32 || pending.at < a.lastTime ||
            pending.at - a.lastTime > 1800)
            return no('noncontiguous-epoch-serial-or-time');
        if (!isLetterDescription(left.Description) || !left.Items || left.Items.length < 2)
            return no('left-type-or-items');
        if (left.Additional.FormFilling !== right.Additional.FormFilling)
            return no('form-state-differs');
        var border = p.length - 2;
        if ((h.SavedIndex !== null && h.SavedIndex !== undefined && h.SavedIndex >= border) ||
            (h.UserSavedIndex !== null && h.UserSavedIndex !== undefined && h.UserSavedIndex >= border))
            return no('saved-boundary');
        // Mirror SDKJS 9.4.0-129 History.CheckUnionLastPoints: disregard the
        // optional TableId_Description prefix on EACH side. Keep actual changes
        // in original order, to support the stock Undo/Redo implementation.
        var lStart = isTableDescription(left.Items[0]) ? 1 : 0;
        var rStart = isTableDescription(right.Items[0]) ? 1 : 0;
        if (left.Items.length - lStart < 1 || right.Items.length - rStart < 1)
            return no('only-table-id-items');
        var info = {epoch:meta.epoch,count:a.count+1,
                    lastSerial:pending.serial,lastTime:pending.at};
        var extra = {ooOvertypeRC3:info};
        if (left.Additional.FormFilling) extra.FormFilling = left.Additional.FormFilling;
        var merged = {State:left.State,
            Items:left.Items.slice(lStart).concat(right.Items.slice(rStart)),
            Time:left.Time,Additional:extra,
            Description:AscDFH.historydescription_Document_AddLetterUnion};
        p.splice(border,2,merged);
        if (h.Index >= p.length) {
            var delta = -h.Index + p.length - 1;
            h.Index += delta;
            h.RecIndex = Math.max(-1,h.RecIndex+delta);
        }
        trace(this,'merged','success',h,merged);
        return true;
    };
})();
