from predictor import predict_house_price
from validation import DEFAULT_FEATURES, FEATURE_COLUMNS


def test_predict_house_price_builds_expected_dataframe():
    captured = {}

    class DummyModel:
        def predict(self, frame):
            captured["columns"] = list(frame.columns)
            captured["first_row"] = frame.iloc[0].to_dict()
            return [321000.5]

    price = predict_house_price(DEFAULT_FEATURES, model=DummyModel())

    assert price == 321000.5
    assert captured["columns"] == FEATURE_COLUMNS
    assert captured["first_row"] == DEFAULT_FEATURES
