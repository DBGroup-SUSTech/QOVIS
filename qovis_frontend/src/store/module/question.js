import {dataService} from '@/service';

// initial state
const state = () => ({
  questions: [
    {
      id: 0,
      target: 'bug0-0', // name of the case
      task: 1,
      approach: 'qv',
      description:
          'As shown in Figure (a), we have a nested column type *Nested* and two tables *tbl* and *ids*.' +
          'The query shown in Figure (b) joins these two tables on the column *id* using *LEFT ANTI JOIN*.' +
          '</br></br>' +
          '![Case 0](figures/issue1_query.png =*x100)\n' +
          '</br></br>' +
          'You are required to **identify the issue** using **our system**. Visit this link to the analysis page: [Case 0](http://localhost:12000/trace?case=0).',
      problem: 'Select the most proper description to this case:', // question
      options: [
        {id: 0, text: 'A. No optimization issue detected.', correct: false},
        {id: 1, text: 'B. Consists of **transformation issue**. The optimizer added a wrong operator *Filter* to the plan.', correct: false},
        {id: 2, text: 'C. Consists of **transformation issue**. The optimizer generated a wrong expression on the operator *Project*.', correct: false},
        {id: 3, text: 'D. Consists of **workflow issue**. A part of optimization steps repeats multiple times but do not change the plan.', correct: true},
      ],
    },
    {
      id: 1,
      target: 'bug0-0', // name of the case
      task: 1,
      approach: 'nm',
      description:
          'As shown in Figure (a), we have a nested column type *Nested* and two tables *tbl* and *ids*.' +
          'The query shown in Figure (b) joins these two tables on the column *id* using *LEFT ANTI JOIN*.' +
          '</br></br>' +
          '![Case 0](figures/issue1_query.png =*x100)\n' +
          '</br></br>' +
          'You are required to **identify the issue** using **the logs**. Go to the log folder and open the log file `Case 0 Log.txt` to analyze.',
      problem: 'Select the most proper description to this case:', // question
      options: [
        {id: 0, text: 'A. No optimization issue detected.', correct: false},
        {id: 1, text: 'B. Consists of **transformation issue**. The optimizer added a wrong operator *Filter* to the plan.', correct: false},
        {id: 2, text: 'C. Consists of **transformation issue**. The optimizer generated a wrong expression on the operator *Project*.', correct: false},
        {id: 3, text: 'D. Consists of **workflow issue**. A part of optimization steps repeats multiple times but do not change the plan.', correct: true},
      ],
    },
    {
      id: 2,
      target: 'bug1-0', // name of the case
      task: 1,
      approach: 'qv',
      description:
          'As shown in Figure (a), we create a data source *ids* with three distinct values.' +
          'The query shown in the below of Figure (a) first derives *ids2* from *ids*, then joins them using *LEFT ANTI JOIN*.' +
          'The expected join logic is shown in Figure (b).' +
          '</br></br>' +
          '![Case 1](figures/issue2_query.png =*x100)\n' +
          '</br></br>' +
          'You are required to **identify the issue** using **our system**. Visit this link to the analysis page: [Case 1](http://localhost:12000/trace?case=1).',
      problem: 'Select the most proper description to this case:', // question
      options: [
        {id: 0, text: 'A. No optimization issue detected.', correct: false},
        {id: 1, text: 'B. Consists of **transformation issue**. The optimizer generated a wrong plan that is not equivalent to the original query after the *Analysis phase*.', correct: false},
        {id: 2, text: 'C. Consists of **transformation issue**. The optimizer generated a wrong plan that is not equivalent to the original query after the *Optimization phase*.', correct: true},
        {id: 3, text: 'D. Consists of **workflow issue**. The optimizer produced two same plans during the *Analysis phase*.', correct: false},
      ],
    },
    {
      id: 3,
      target: 'bug1-0', // name of the case
      task: 2,
      approach: 'nm',
      description:
          'As shown in Figure (a), we create a data source *ids* with three distinct values.' +
          'The query shown in the below of Figure (a) first derives *ids2* from *ids*, then joins them using *LEFT ANTI JOIN*.' +
          'The expected join logic is shown in Figure (b).' +
          '</br></br>' +
          '![Case 1](figures/issue2_query.png =*x100)\n' +
          '</br></br>' +
          'You are required to **identify the issue** using **the logs**. Go to the log folder and open the log file `Case 1 Log.txt` to analyze.',
      problem: 'Select the most proper description to this case:', // question
      options: [
        {id: 0, text: 'A. No optimization issue detected.', correct: false},
        {id: 1, text: 'B. Consists of **transformation issue**. The optimizer generated a wrong plan that is not equivalent to the original query after the *Analysis phase*.', correct: false},
        {id: 2, text: 'C. Consists of **transformation issue**. The optimizer generated a wrong plan that is not equivalent to the original query after the *Optimization phase*.', correct: true},
        {id: 3, text: 'D. Consists of **workflow issue**. The optimizer produced two same plans during the *Analysis phase*.', correct: false},
      ],
    },
    {
      id: 4,
      target: 'ssb-q1', // name of the case
      task: 1,
      approach: 'qv',
      description:
          'As shown in Figure (a), this query joins two tables *lo_orderdate* and *date* with multiple predicates.' +
          '</br></br>' +
          '![Case 2](figures/norm1_query.png =*x100)\n' +
          '</br></br>' +
          'You are required to **identify the issue** using **our system**. Visit this link to the analysis page: [Case 2](http://localhost:12000/trace?case=2).',
      problem: 'Select the most proper description to this case:', // question
      options: [
        {id: 0, text: 'A. No optimization issue detected.', correct: true},
        {id: 1, text: 'B. Consists of **transformation issue**. The optimizer generated a wrong plan that is not equivalent to the original query after the *Analysis phase*.', correct: false},
        {id: 2, text: 'C. Consists of **transformation issue**. The optimizer generated a wrong plan that is not equivalent to the original query after the *Optimization phase*.', correct: true},
        {id: 3, text: 'D. Consists of **workflow issue**. The optimizer conducted two same steps in *Analysis phase*.', correct: false},
      ],
    },
    {
      id: 5,
      target: 'ssb-q1', // name of the case
      task: 1,
      approach: 'nv',
      description:
          'As shown in Figure (a), this query joins two tables *lo_orderdate* and *date* with multiple predicates.' +
          '</br></br>' +
          '![Case 2](figures/norm1_query.png =*x100)\n' +
          '</br></br>' +
          'You are required to **identify the issue** using **the logs**. Go to the log folder and open the log file `Case 2 Log.txt` to analyze.',
      problem: 'Select the most proper description to this case:', // question
      options: [
        {id: 0, text: 'A. No optimization issue detected.', correct: true},
        {id: 1, text: 'B. Consists of **transformation issue**. The optimizer generated a wrong plan that is not equivalent to the original query after the *Optimization phase*.', correct: false},
        {id: 2, text: 'C. Consists of **transformation issue**. The optimizer generated a wrong plan that is not equivalent to the original query after the *Analysis phase*.', correct: false},
        {id: 3, text: 'D. Consists of **workflow issue**. The optimizer conducted two same steps in *Analysis phase*.', correct: false},
      ],
    },
    {
      id: 6,
      target: 'ssb-q11', // name of the case
      task: 1,
      approach: 'qv',
      description:
          'As shown in Figure (a), this query joins two tables *lo_orderdate* and *date* with multiple predicates.' +
          '</br></br>' +
          '![Case 3](figures/norm2_query.png =*x100)\n' +
          '</br></br>' +
          'You are required to **identify the issue** using **our system**. Visit this link to the analysis page: [Case 3](http://localhost:12000/trace?case=3).',
      problem: 'Select the most proper description to this case:', // question
      options: [
        {id: 0, text: 'A. No optimization issue detected.', correct: true},
        {id: 1, text: 'B. Consists of **transformation issue**. The optimizer generated a wrong plan that is not equivalent to the original query after the *Analysis phase*.', correct: false},
        {id: 2, text: 'C. Consists of **transformation issue**. The optimizer generated a wrong plan that is not equivalent to the original query after the *Optimization phase*.', correct: false},
        {id: 3, text: 'D. Consists of **workflow issue**. The optimizer conducted two same steps in *Optimization phase*.', correct: false},
      ],
    },
    {
      id: 7,
      target: 'ssb-q11', // name of the case
      task: 1,
      approach: 'nv',
      description:
          'As shown in Figure (a), this query joins two tables *lo_orderdate* and *date* with multiple predicates.' +
          '</br></br>' +
          '![Case 3](figures/norm2_query.png =*x100)\n' +
          '</br></br>' +
          'You are required to **identify the issue** using **the logs**. Go to the log folder and open the log file `Case 3 Log.txt` to analyze.',
      problem: 'Select the most proper description to this case:', // question
      options: [
        {id: 0, text: 'A. No optimization issue detected.', correct: true},
        {id: 1, text: 'B. Consists of **transformation issue**. The optimizer generated a wrong plan that is not equivalent to the original query after the *Optimization phase*.', correct: false},
        {id: 2, text: 'C. Consists of **transformation issue**. The optimizer generated a wrong plan that is not equivalent to the original query after the *Analysis phase*.', correct: false},
        {id: 3, text: 'D. Consists of **workflow issue**. The optimizer conducted two same steps in *Optimization phase*.', correct: false},
      ],
    },

    {
      id: 8,
      target: 'bug0-0', // name of the case
      task: 2,
      approach: 'qv',
      description:
          'As shown in Figure (a), we have a nested column type *Nested* and two tables *tbl* and *ids*.' +
          'The query shown in Figure (b) joins these two tables on the column *id* using *LEFT ANTI JOIN*.' +
          '</br></br>' +
          '![Case 0](figures/issue1_query.png =*x100)\n' +
          '</br></br>' +
          'This case consists of a **workflow issue**. A part of optimization steps repeats multiple times but do not change the plan (As show in below). This is an optimization loop and most of the steps are useless.' +
          '</br></br>' +
          '![Case 0 - the loop](figures/issue1_1.png =*x150)\n' +
          '![Case 0 - the loop](figures/issue1_2.png =*x150)\n' +
          '</br></br>' +
          'You are required to **locate the root cause** using **our system**. Visit this link to the analysis page: [Case 0](http://localhost:12000/trace?case=0).',
      problem: 'Select the most proper description to this case:', // question
      options: [
        {id: 0, text: 'A. The root cause is that *InferFilterFromConstraints* step inserts a useless filter and the optimizer continue to rewrite the plan.', correct: false},
        {id: 1, text: 'B. The root cause is that *ColumnPruning* step in the previous loop and *CollapseProject* in the next loop generate/consume two *Project* nodes, so they cancel each other out.', correct: true},
        {id: 2, text: 'C. The root cause is that *PushDownLeftSemiAntiJoin* step does not push down the *leftAntiJoin* successfully so that the optimizer try to optimize it again.', correct: false},
        {id: 3, text: 'D. The root cause is that *ColumnPruning* step and *RemoveNoopOperators* step add/remove a *Project* node so that the optimizer continue optimizing.', correct: false},
      ],
    },
    {
      id: 9,
      target: 'bug0-0', // name of the case
      task: 2,
      approach: 'nm',
      description:
          'As shown in Figure (a), we have a nested column type *Nested* and two tables *tbl* and *ids*.' +
          'The query shown in Figure (b) joins these two tables on the column *id* using *LEFT ANTI JOIN*.' +
          '</br></br>' +
          '![Case 0](figures/issue1_query.png =*x100)\n' +
          '</br></br>' +
          'This case consists of a **workflow issue**. A part of optimization steps repeats multiple times but do not change the plan (As show in below). This is an optimization loop and most of the steps are useless.' +
          '</br></br>' +
          '![Case 0 - the loop](figures/issue1_1.png =*x150)\n' +
          '![Case 0 - the loop](figures/issue1_2.png =*x150)\n' +
          '</br></br>' +
          'You are required to **locate the root cuase** using **the logs**. Go to the log folder and open the log file `Case 0 Log.txt` to analyze.',
      problem: 'Select the most proper description to this case:', // question
      options: [
        {id: 0, text: 'A. The root cause is that *InferFilterFromConstraints* step inserts a useless filter and the optimizer continue to rewrite the plan.', correct: false},
        {id: 1, text: 'B. The root cause is that *ColumnPruning* step in the previous loop and *CollapseProject* in the next loop generate/consume two *Project* nodes, so they cancel each other out.', correct: true},
        {id: 2, text: 'C. The root cause is that *PushDownLeftSemiAntiJoin* step does not push down the *leftAntiJoin* successfully so that the optimizer try to optimize it again.', correct: false},
        {id: 3, text: 'D. The root cause is that *ColumnPruning* step and *RemoveNoopOperators* step add/remove a *Project* node so that the optimizer continue optimizing.', correct: false},
      ],
    },
    {
      id: 2,
      target: 'bug1-0', // name of the case
      task: 1,
      approach: 'qv',
      description:
          'As shown in Figure (a), we create a data source *ids* with three distinct values.' +
          'The query shown in the below of Figure (a) first derives *ids2* from *ids*, then joins them using *LEFT ANTI JOIN*.' +
          'The expected join logic is shown in Figure (b).' +
          '</br></br>' +
          '![Case 1](figures/issue2_query.png =*x100)\n' +
          '</br></br>' +
          'You are required to **identify the issue** using **our system**. Visit this link to the analysis page: [Case 1](http://localhost:12000/trace?case=1).',
      problem: 'Select the most proper description to this case:', // question
      options: [
        {id: 0, text: 'A. No optimization issue detected.', correct: false},
        {id: 1, text: 'B. Consists of **transformation issue**. The optimizer generated a wrong plan that is not equivalent to the original query after the *Analysis phase*.', correct: false},
        {id: 2, text: 'C. Consists of **transformation issue**. The optimizer generated a wrong plan that is not equivalent to the original query after the *Optimization phase*.', correct: true},
        {id: 3, text: 'D. Consists of **workflow issue**. The optimizer produced two same plans during the *Analysis phase*.', correct: false},
      ],
    },
    {
      id: 3,
      target: 'bug1-0', // name of the case
      task: 2,
      approach: 'nm',
      description:
          'As shown in Figure (a), we create a data source *ids* with three distinct values.' +
          'The query shown in the below of Figure (a) first derives *ids2* from *ids*, then joins them using *LEFT ANTI JOIN*.' +
          'The expected join logic is shown in Figure (b).' +
          '</br></br>' +
          '![Case 1](figures/issue2_query.png =*x100)\n' +
          '</br></br>' +
          'You are required to **identify the issue** using **the logs**. Go to the log folder and open the log file `Case 1 Log.txt` to analyze.',
      problem: 'Select the most proper description to this case:', // question
      options: [
        {id: 0, text: 'A. No optimization issue detected.', correct: false},
        {id: 1, text: 'B. Consists of **transformation issue**. The optimizer generated a wrong plan that is not equivalent to the original query after the *Analysis phase*.', correct: false},
        {id: 2, text: 'C. Consists of **transformation issue**. The optimizer generated a wrong plan that is not equivalent to the original query after the *Optimization phase*.', correct: true},
        {id: 3, text: 'D. Consists of **workflow issue**. The optimizer produced two same plans during the *Analysis phase*.', correct: false},
      ],
    },

    {
      id: 4,
      target: 'ssb-q1', // name of the case
      task: 1,
      approach: 'qv',
      description:
          'As shown in Figure (a), this query joins two tables *lo_orderdate* and *date* with multiple predicates.' +
          '</br></br>' +
          '![Case 2](figures/norm1_query.png =*x100)\n' +
          '</br></br>' +
          'You are required to **identify the issue** using **our system**. Visit this link to the analysis page: [Case 2](http://localhost:12000/trace?case=2).',
      problem: 'Select the most proper description to this case:', // question
      options: [
        {id: 0, text: 'A. No optimization issue detected.', correct: true},
        {id: 1, text: 'B. Consists of **transformation issue**. The optimizer generated a wrong plan that is not equivalent to the original query after the *Analysis phase*.', correct: false},
        {id: 2, text: 'C. Consists of **transformation issue**. The optimizer generated a wrong plan that is not equivalent to the original query after the *Optimization phase*.', correct: true},
        {id: 3, text: 'D. Consists of **workflow issue**. The optimizer conducted two same steps in *Analysis phase*.', correct: false},
      ],
    },
    {
      id: 5,
      target: 'ssb-q1', // name of the case
      task: 1,
      approach: 'nv',
      description:
          'As shown in Figure (a), this query joins two tables *lo_orderdate* and *date* with multiple predicates.' +
          '</br></br>' +
          '![Case 2](figures/norm1_query.png =*x100)\n' +
          '</br></br>' +
          'You are required to **identify the issue** using **the logs**. Go to the log folder and open the log file `Case 2 Log.txt` to analyze.',
      problem: 'Select the most proper description to this case:', // question
      options: [
        {id: 0, text: 'A. No optimization issue detected.', correct: true},
        {id: 1, text: 'B. Consists of **transformation issue**. The optimizer generated a wrong plan that is not equivalent to the original query after the *Optimization phase*.', correct: false},
        {id: 2, text: 'C. Consists of **transformation issue**. The optimizer generated a wrong plan that is not equivalent to the original query after the *Analysis phase*.', correct: false},
        {id: 3, text: 'D. Consists of **workflow issue**. The optimizer conducted two same steps in *Analysis phase*.', correct: false},
      ],
    },
    {
      id: 6,
      target: 'ssb-q11', // name of the case
      task: 1,
      approach: 'qv',
      description:
          'As shown in Figure (a), this query joins two tables *lo_orderdate* and *date* with multiple predicates.' +
          '</br></br>' +
          '![Case 3](figures/norm2_query.png =*x100)\n' +
          '</br></br>' +
          'You are required to **identify the issue** using **our system**. Visit this link to the analysis page: [Case 3](http://localhost:12000/trace?case=3).',
      problem: 'Select the most proper description to this case:', // question
      options: [
        {id: 0, text: 'A. No optimization issue detected.', correct: true},
        {id: 1, text: 'B. Consists of **transformation issue**. The optimizer generated a wrong plan that is not equivalent to the original query after the *Analysis phase*.', correct: false},
        {id: 2, text: 'C. Consists of **transformation issue**. The optimizer generated a wrong plan that is not equivalent to the original query after the *Optimization phase*.', correct: false},
        {id: 3, text: 'D. Consists of **workflow issue**. The optimizer conducted two same steps in *Optimization phase*.', correct: false},
      ],
    },
    {
      id: 7,
      target: 'ssb-q11', // name of the case
      task: 1,
      approach: 'nv',
      description:
          'As shown in Figure (a), this query joins two tables *lo_orderdate* and *date* with multiple predicates.' +
          '</br></br>' +
          '![Case 3](figures/norm2_query.png =*x100)\n' +
          '</br></br>' +
          'You are required to **identify the issue** using **the logs**. Go to the log folder and open the log file `Case 3 Log.txt` to analyze.',
      problem: 'Select the most proper description to this case:', // question
      options: [
        {id: 0, text: 'A. No optimization issue detected.', correct: true},
        {id: 1, text: 'B. Consists of **transformation issue**. The optimizer generated a wrong plan that is not equivalent to the original query after the *Optimization phase*.', correct: false},
        {id: 2, text: 'C. Consists of **transformation issue**. The optimizer generated a wrong plan that is not equivalent to the original query after the *Analysis phase*.', correct: false},
        {id: 3, text: 'D. Consists of **workflow issue**. The optimizer conducted two same steps in *Optimization phase*.', correct: false},
      ],
    },
  ],
  submitted: false,
})

// getters
const getters = {}

// actions
const actions = {
  postResult({commit}, {result, vueComponent}) {
    const errorFunc = error => {
      vueComponent.$message({
        showClose: true,
        message: 'Failed to submit your answer. Please save your file to local. ' + error,
        type: 'error'
      })
    }
    dataService.postQuestionData(result, resp => {
      if (resp === '') {
        commit('changeSubmitted', true)
      } else {
        errorFunc(resp)
      }
    }, error => {
      errorFunc(error)
    })
  },
}

// mutations
const mutations = {
  changeSubmitted(state, submitted) {
    state.submitted = submitted
  }
}

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
}
