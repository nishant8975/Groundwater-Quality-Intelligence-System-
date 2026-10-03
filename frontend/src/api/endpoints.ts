import { apiClient } from './client';
import type { ApiResponse, OverviewStats } from '../types';

export const fetchOverview = (): Promise<ApiResponse<OverviewStats>> => {
  return apiClient.get('/overview');
};

export const fetchCategories = (): Promise<ApiResponse<any[]>> => {
  return apiClient.get('/wawqi/categories');
};

export const fetchStates = (): Promise<ApiResponse<any[]>> => {
  return apiClient.get('/states');
};

export const fetchStateDetail = (state: string): Promise<ApiResponse<any>> => {
  return apiClient.get(`/states/${encodeURIComponent(state)}`);
};

export const fetchDistricts = (params: any = {}): Promise<ApiResponse<any[]>> => {
  return apiClient.get('/districts', { params });
};

export const fetchDistrictDetail = (district: string, state?: string): Promise<ApiResponse<any[]>> => {
  return apiClient.get(`/districts/${encodeURIComponent(district)}`, { params: { state } });
};

export const fetchParameters = (): Promise<ApiResponse<any[]>> => {
  return apiClient.get('/parameters');
};

export const fetchParameterDetail = (parameter: string, params: any = {}): Promise<ApiResponse<any[]>> => {
  return apiClient.get(`/parameters/${encodeURIComponent(parameter)}`, { params });
};

export const fetchExceedances = (params: any = {}): Promise<ApiResponse<any[]>> => {
  return apiClient.get('/exceedances', { params });
};

export const fetchExtremes = (params: any = {}): Promise<ApiResponse<any[]>> => {
  return apiClient.get('/extremes', { params });
};

export const fetchDataQuality = (): Promise<ApiResponse<any>> => {
  return apiClient.get('/data-quality');
};

export const fetchTemporal = (): Promise<ApiResponse<any[]>> => {
  return apiClient.get('/temporal');
};

export const fetchGis = (params: any = {}): Promise<ApiResponse<any[]>> => {
  return apiClient.get('/gis', { params });
};

export const fetchStations = (params: any = {}): Promise<ApiResponse<any[]>> => {
  return apiClient.get('/stations', { params });
};

export const fetchStationDetail = (hash: string): Promise<ApiResponse<any>> => {
  return apiClient.get(`/stations/${hash}`);
};

export const fetchStationHistory = (hash: string): Promise<ApiResponse<any[]>> => {
  return apiClient.get(`/stations/${hash}/history`);
};

export const fetchStationParameters = (hash: string): Promise<ApiResponse<any[]>> => {
  return apiClient.get(`/stations/${hash}/parameters`);
};

