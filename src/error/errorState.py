from src.type.VDA5050 import state


def error(error_type, error_level, reference_key, reference_value, error_description=""):
    return state.Error(
        errorType=error_type,
        errorLevel=error_level,
        errorReferences=[state.ErrorReference(
            referenceKey=reference_key,
            referenceValue=reference_value
        )],
        errorDescription=error_description
    )


class ErrorState:
    """
    use for return a error of state
    """
