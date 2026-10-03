import { useQuery } from '@tanstack/react-query';
import { 
  fetchOverview, fetchCategories, fetchStates, fetchStateDetail, 
  fetchDistricts, fetchDistrictDetail, fetchParameters, 
  fetchParameterDetail, fetchExceedances, fetchExtremes, 
  fetchDataQuality, fetchTemporal, fetchGis,
  fetchStations, fetchStationDetail, fetchStationHistory, fetchStationParameters
} from '../api/endpoints';

export const useOverview = () => useQuery({ queryKey: ['overview'], queryFn: fetchOverview });
export const useCategories = () => useQuery({ queryKey: ['categories'], queryFn: fetchCategories });
export const useStates = () => useQuery({ queryKey: ['states'], queryFn: fetchStates });
export const useStateDetail = (state: string) => useQuery({ queryKey: ['state', state], queryFn: () => fetchStateDetail(state), enabled: !!state });
export const useDistricts = (filters: any = {}) => useQuery({ queryKey: ['districts', filters], queryFn: () => fetchDistricts(filters) });
export const useDistrictDetail = (district: string, state?: string) => useQuery({ queryKey: ['district', district, state], queryFn: () => fetchDistrictDetail(district, state), enabled: !!district });
export const useParameters = () => useQuery({ queryKey: ['parameters'], queryFn: fetchParameters });
export const useParameterDetail = (parameter: string, filters: any = {}) => useQuery({ queryKey: ['parameter', parameter, filters], queryFn: () => fetchParameterDetail(parameter, filters), enabled: !!parameter });
export const useExceedances = (filters: any = {}) => useQuery({ queryKey: ['exceedances', filters], queryFn: () => fetchExceedances(filters) });
export const useExtremes = (filters: any = {}) => useQuery({ queryKey: ['extremes', filters], queryFn: () => fetchExtremes(filters) });
export const useDataQuality = () => useQuery({ queryKey: ['dataQuality'], queryFn: fetchDataQuality });
export const useTemporal = () => useQuery({ queryKey: ['temporal'], queryFn: fetchTemporal });
export const useGis = (filters: any = {}) => useQuery({ queryKey: ['gis', filters], queryFn: () => fetchGis(filters) });
export const useStations = (filters: any = {}) => useQuery({ queryKey: ['stations', filters], queryFn: () => fetchStations(filters) });
export const useStationDetail = (hash: string) => useQuery({ queryKey: ['stationDetail', hash], queryFn: () => fetchStationDetail(hash), enabled: !!hash });
export const useStationHistory = (hash: string) => useQuery({ queryKey: ['stationHistory', hash], queryFn: () => fetchStationHistory(hash), enabled: !!hash });
export const useStationParameters = (hash: string) => useQuery({ queryKey: ['stationParameters', hash], queryFn: () => fetchStationParameters(hash), enabled: !!hash });

