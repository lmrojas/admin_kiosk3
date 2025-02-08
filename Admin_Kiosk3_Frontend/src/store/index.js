import { configureStore } from '@reduxjs/toolkit';
import kioskReducer from './kioskSlice';
import authReducer from './authSlice';

export const store = configureStore({
  reducer: {
    kiosks: kioskReducer,
    auth: authReducer
  }
}); 