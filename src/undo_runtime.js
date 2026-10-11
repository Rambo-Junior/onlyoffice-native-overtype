/*
 * ONLYOFFICE Overtype native RC2: opt-in Undo grouping, SDKJS v9.4.0.129 only.
 * No edit or selection mutation: grouping only already-finalized history points.
 * SPDX-License-Identifier: AGPL-3.0-only
 */
(function() {
    "use strict";
    var historyPrototype = AscCommon.CHistory && AscCommon.CHistory.prototype;
    if (!historyPrototype || typeof historyPrototype.CheckUnionLastPoints !== "function")
        throw new Error("OO_OVERTYPE_UNDO_RC2: unknown ONLYOFFICE history API");
    if (historyPrototype._ooOvertypeUndoRC2)
        throw new Error("OO_OVERTYPE_UNDO_RC2: duplicate installation");
    var original = historyPrototype.CheckUnionLastPoints;
    historyPrototype._ooOvertypeUndoRC2 = true;
    historyPrototype.CheckUnionLastPoints = function() {
        var pts = this.Points, len = pts && pts.length;
        // Keep the upstream guard semantics (active action, redo state, saves).
        if (len < 2 || this.Index !== len - 1 || this.UndoRedoInProgress ||
            (this.Document && (!this.Document.Is_OnRecalculate() || this.Document.IsActionStarted())))
            return original.apply(this, arguments);
        if ((this.Is_UserSaveMode && this.Is_UserSaveMode()) ?
            (this.UserSavedIndex !== null && this.UserSavedIndex >= len - 2) :
            (this.SavedIndex !== null && this.SavedIndex >= len - 2))
            return original.apply(this, arguments);
        var left = pts[len-2], right = pts[len-1];
        if (!left || !right || !left.Additional || !right.Additional)
            return original.apply(this, arguments);
        var a = left.Additional.ooOvertypeRC2, b = right.Additional.ooOvertypeRC2;
        if (!a || !b || a.epoch !== b.epoch ||
            !Number.isSafeInteger(a.count) || a.count < 1 || a.count >= 32 ||
            b.count !== 1 || b.lastSerial !== a.lastSerial + 1 ||
            b.time < a.lastTime || b.time - a.lastTime > 1800 ||
            left.Additional.FormFilling !== right.Additional.FormFilling ||
            !left.Items || !left.Items.length || !right.Items || !right.Items.length)
            return original.apply(this, arguments);
        // Only group the native overtype actions; other edits retain stock Undo.
        if (left.Description !== AscDFH.historydescription_Document_AddLetter ||
            right.Description !== AscDFH.historydescription_Document_AddLetter)
            return original.apply(this, arguments);
        // Do not silently reorder table-id/structural history metadata.
        if ((left.Items[0].Data && left.Items[0].Data.Type === AscDFH.historyitem_TableId_Description) ||
            (right.Items[0].Data && right.Items[0].Data.Type === AscDFH.historyitem_TableId_Description))
            return original.apply(this, arguments);
        var merged = {
            State: left.State,
            Items: left.Items.concat(right.Items),
            Time: left.Time,
            Additional: {ooOvertypeRC2: {
                epoch: a.epoch, count: a.count + 1,
                lastTime: b.time, lastSerial: b.lastSerial
            }},
            Description: left.Description
        };
        if (left.Additional.FormFilling)
            merged.Additional.FormFilling = left.Additional.FormFilling;
        // Identical Index/RecIndex bookkeeping to upstream CheckUnionLastPoints().
        pts.splice(len - 2, 2, merged);
        if (this.Index >= pts.length) {
            var diff = -this.Index + (pts.length - 1);
            this.Index += diff;
            this.RecIndex = Math.max(-1, this.RecIndex + diff);
        }
        return true;
    };
})();
CDocument.prototype._ooMarkOvertypeUndoPoint = function() {
    var history = this.History;
    if (!history || !history.Points || history.Index < 0) return;
    var point = history.Points[history.Index];
    if (!point || !point.Additional) return;
    var serial = (this._ooOvertypeUndoSerial || 0) + 1;
    this._ooOvertypeUndoSerial = serial;
    point.Additional.ooOvertypeRC2 = {
        epoch: this._ooOvertypeUndoEpoch || 0,
        count: 1, lastSerial: serial, time: Date.now(), lastTime: Date.now()
    };
};
