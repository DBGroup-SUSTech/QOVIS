import axios from 'axios'

const URL_PREFIX = '/api';

export function getExampleList(callback) {
  const url=`${URL_PREFIX}/example-list`;
  axios.get(url)
    .then(response =>{
      callback(response.data)
    }, errResponse => {
      console.log(errResponse)
    })
}

export function getTraceData(exampleName, callback) {
  const url=`${URL_PREFIX}/trace-data`;
  const params = {'example_name': exampleName}
  axios.get(url, {params})
    .then(response => {
      callback(response.data)
    }, errResponse => {
      console.log(errResponse)
    })
}

export function getDynamicGraph(exampleName, callback) {
  const url=`${URL_PREFIX}/dynamic-graph`;
  const params = {'example_name': exampleName}
  axios.get(url, {params})
      .then(response => {
        callback(response.data)
      }, errResponse => {
        console.log(errResponse)
      })
}

export function getSummaryList(exampleName, callback) {
  const url=`${URL_PREFIX}/summary-list`;
  const params = {'example_name': exampleName}
  axios.get(url, {params})
      .then(response => {
        callback(response.data)
      }, errResponse => {
        console.log(errResponse)
      })
}

export function getSummaryData(exampleName, summaryName, callback) {
  const url=`${URL_PREFIX}/summary-data`;
  const params = {'example_name': exampleName, 'summary_name': summaryName}
  console.log('>>>', params)
  axios.get(url, {params})
      .then(response => {
        callback(response.data)
      }, errResponse => {
        console.log(errResponse)
      })
}

export function getOptInfoList(callback) {
  const url=`${URL_PREFIX}/opt-data`
  axios.get(url, {})
      .then(response => {
        callback(response.data)
      }, errResponse => {
        console.log(errResponse)
      })
}

export function getProbeList(callback) {
  const url=`${URL_PREFIX}/probe-list`
  axios.get(url, {})
      .then(response => {
        callback(response.data)
      }, errResponse => {
        console.log(errResponse)
      })
}

export function getProbeData(probeName, callback) {
  const url=`${URL_PREFIX}/probe-data`
  const params = {'probe_name': probeName}
  axios.get(url, {params})
      .then(response => {
        callback(response.data)
      }, errResponse => {
        console.log(errResponse)
      })
}

export function postQuestionData(data, callback, errCallback) {
  const url=`${URL_PREFIX}/question-result`
  axios.post(url, data)
      .then(response => {
        callback(response.data)
      }, errResponse => {
        console.log(errResponse)
        errCallback(errResponse)
      })
}

