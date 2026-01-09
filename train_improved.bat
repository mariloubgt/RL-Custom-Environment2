@echo off
REM Improved training configuration for A2C
REM This script uses better hyperparameters for more stable training

python training/train_a2c.py --episodes 2000 --resume-from models/a2c_model_final.pth --lr 0.0001 --gamma 0.99 --value-coef 0.7 --entropy-coef 0.05 --save-freq 200

