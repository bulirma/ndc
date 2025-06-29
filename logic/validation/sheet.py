class SheetCollectionValidationResult:
    light_condition_valid = False
    quality_valid = False

    def is_valid(self) -> bool:
        return self.light_condition_valid and self.quality_valid

def validate_sheet_collection_data(form_data: dict) -> SheetCollectionValidationResult:
    result = SheetCollectionValidationResult()
    if form_data['light-condition'] in ('dark', 'dimmed', 'light', 'flashlight'):
        result.light_condition_valid = True
    if form_data['quality'] in ('poor', 'satisfactory', 'good'):
        result.quality_valid = True
    return result
