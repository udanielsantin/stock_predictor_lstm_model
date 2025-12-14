import torch
import torch.nn as nn
import joblib
from pathlib import Path

class StockLSTM(nn.Module):
    def __init__(self, input_size=1, hidden_size=64, num_layers=2):
        super().__init__()
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True)
        self.fc = nn.Linear(hidden_size, 1)

    def forward(self, x):
        out, _ = self.lstm(x)
        out = self.fc(out[:, -1, :])
        return out


def load_artifacts(artifacts_dir: str = "artifacts"):
    artifacts_dir = Path(artifacts_dir)
    model_path = artifacts_dir / "stock_lstm.pt"
    scaler_path = artifacts_dir / "scaler.joblib"
    if not model_path.exists() or not scaler_path.exists():
        raise FileNotFoundError("Artifacts not found. Train notebook and save artifacts first.")
    model = StockLSTM()
    state = torch.load(model_path, map_location="cpu")
    model.load_state_dict(state)
    model.eval()
    scaler = joblib.load(scaler_path)
    return model, scaler


def predict_next(model: nn.Module, scaler, seq):
    # seq: list/array of last 50 scaled close values shape (50, 1)
    import numpy as np
    t = torch.tensor(np.asarray(seq), dtype=torch.float32).unsqueeze(0)
    with torch.no_grad():
        pred_scaled = model(t).numpy()
    pred = scaler.inverse_transform(pred_scaled)[0][0]
    return float(pred)
