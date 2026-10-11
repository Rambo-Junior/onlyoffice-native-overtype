/*
 * EXPERIMENTAL ONLYOFFICE SDKJS Overtype prototype
 * Apply only to source code, never directly to an installed editor.
 * SPDX-License-Identifier: AGPL-3.0-only
 */
CDocument.prototype._ooTryOvertypeOne = function() {
    // Fail closed: never attempt to overwrite an existing selection or an embedded object.
    if (this.IsSelectionUse() || !this.GetCurrentParagraph || !this.GetSelectedElementsInfo)
        return false;
    if (this.IsTrackRevisions && this.IsTrackRevisions())
        return false;
    if (this.IsFillingFormMode && this.IsFillingFormMode())
        return false;

    let selectedInfo = this.GetSelectedElementsInfo();
    if (!selectedInfo)
        return false;
    if ((selectedInfo.IsInTable && selectedInfo.IsInTable())
        || (selectedInfo.GetMath && selectedInfo.GetMath())
        || (selectedInfo.GetCheckBox && selectedInfo.GetCheckBox())
        || (selectedInfo.IsDrawingObjSelected && selectedInfo.IsDrawingObjSelected())
        || (selectedInfo.IsMixedSelection && selectedInfo.IsMixedSelection()))
        return false;

    let paragraph = this.GetCurrentParagraph();
    if (!paragraph || !paragraph.IsCursorAtEnd || !paragraph.getCurrentPos
        || !paragraph.Get_RightPos || !paragraph.SetSelectionContentPos
        || !paragraph.GetSelectedText)
        return false;
    if (paragraph.IsCursorAtEnd())
        return false;

    if (this.Document_Is_SelectionLocked
        && this.Document_Is_SelectionLocked(AscCommon.changestype_Remove, null, true, this.IsFormFieldEditing()))
        return false;

    let state = this.SaveDocumentState(false);
    try {
        let start = paragraph.getCurrentPos();
        let next = new CParagraphSearchPos();
        paragraph.Get_RightPos(next, start, false);
        if (!next.IsFound()) {
            this.LoadDocumentState(state);
            return false;
        }
        paragraph.SetSelectionContentPos(start, next.GetPos().Copy(), false);
        let selectedText = paragraph.GetSelectedText(true);
        // Do not remove paragraph boundaries, line breaks, or multi-codepoint graphemes.
        // Combining marks are deliberately rejected until grapheme segmentation is validated.
        if (typeof selectedText !== 'string' || Array.from(selectedText).length !== 1
            || /[\r\n\u2028\u2029]/.test(selectedText)
            || /\p{Mark}/u.test(selectedText)) {
            this.LoadDocumentState(state);
            return false;
        }
        // Selection has been validated, with no document mutation yet.
    } catch (error) {
        this.LoadDocumentState(state);
        return false;
    }
    // Both deletion and insertion happen inside the caller's single StartAction.
    // Never swallow a failed Remove: it could leave the document in a mutated state.
    this.Remove(1, true, false, true);
    return true;
};
