import {Question} from "@/js/question/Question"

export const QuestionList = [
  new Question(
      'bug4-0',   // I1
      1,
      'As shown in Figure (a), the query filters the data in the table *t* using *EXISTS* clause, only remaining rows that exist in another table *s*. ' +
      'As the table *t* is a small table, a hint */\\*+ BROADCAST(t) \\*/* is given. ' +
      'The optmizer rewrites the query using *LEFT SEMI JOIN* (as shown in Figure (b)) and the table *t* will be broadcased while executing. ' +
      '</br></br>' +
      '![Case 1](figures/issue3_query.png =*x100)' +
      '</br></br>' +
      'Tips: In normal cases, *Broadcaset hint* will be processed as follows: ' +
      '</br>As a single node *ResolvedHint* in the plan in *Analysis phase*;' +
      '</br>Be set to join node in *Optimization phase*;' +
      '</br>Convert to a *BroadcastExchange* node in *Planning phase*.',
      'Select the most proper description to this case:',
      [
        {id: 0, text: 'A. No optimization issue detected.'},
        {id: 1, text: 'B. Consists of **transformation issue**. The *broadcast hint* is missing in the analyzed plan and the executor broadcasts another table *s*.'},
        {id: 2, text: 'C. Consists of **transformation issue**. The optimizer fails to convert *EXISTS* to *LEFT SEMI JOIN* during the *Optimization phase*.'},
        {id: 3, text: 'D. Consists of **workflow issue**. Rule *RemoveNoopOperators* does not remove useless *Project* node on the top of the plan.'},
      ],
      1
  ),
  new Question(
      'ssb-q1',   // N0
      1,
      'As shown in Figure (a), this query joins two tables *lineorder* and *date* with multiple predicates. ' +
      'Then two of the attributes are used in the *sum* expression. ' +
      '</br></br>' +
      '![Case 3](figures/norm1_query.png =*x150)\n',
      'Select the most proper description to this case:',
      [
        {id: 0, text: 'A. No optimization issue detected.'},
        {id: 1, text: 'B. Consists of **transformation issue**. A wrong aggregate function is generated in the *Aggregate* node after the *Analysis phase*.'},
        {id: 2, text: 'C. Consists of **transformation issue**. A wrong join condition is added to the *InnerJoin* during the *Optimization phase*.'},
        {id: 3, text: 'D. Consists of **workflow issue**. Few redundant steps repeat multiple times in *Optimization phase*.'},
      ],
      0
  ),
  new Question(
      'bug1-0',   // I2
      1,
      'As shown in Figure (a), there is a data source *ids* with three distinct values. ' +
      'The query shown in the below of Figure (a) first derives *ids2* from *ids*, then joins them using *LEFT ANTI JOIN*. ' +
      'The expected join logic is shown in Figure (b). ' +
      '</br></br>' +
      '![Case 2](figures/issue2_query.png =*x180)\n',
      'Select the most proper description to this case:',
      [
        {id: 0, text: 'A. No optimization issue detected.'},
        {id: 1, text: 'B. Consists of **transformation issue**. A wrong analyzed plan is generated, which is not equivalent to the original query.'},
        {id: 2, text: 'C. Consists of **transformation issue**. A wrong optimized plan is generated, which is not equivalent to the original query.'},
        {id: 3, text: 'D. Consists of **workflow issue**. *DeduplicateRelations* step in *Analysis phase* does not change the single data source into different one.'},
      ],
      2
  ),
  new Question(
      'ssb-q11',    // N1
      1,
      'As shown in Figure (a), this query joins five tables together with multiple predicates. ' +
      'Then the data is grouped by *d\\_year* and *c\\_nation*. ' +
      '</br></br>' +
      '![Case 4](figures/norm3_query.png =*x200)\n',
      'Select the most proper description to this case:',
      [
        {id: 0, text: 'A. No optimization issue detected.'},
        {id: 1, text: 'B. Consists of **transformation issue**. The optimized plan after *Optimization phase* does not join 5 tables.'},
        {id: 2, text: 'C. Consists of **transformation issue**. One *InnerJoin* condition on optimized plan is not derived from the predicates in the *Filter* of analyzed plan.'},
        {id: 3, text: 'D. Consists of **workflow issue**. *ReorderJoin* is conducted twice continuously at the start of *Optimization phase*.'},
      ],
      0
  ),
  new Question(
      'bug0-0',   // I0
      1,
      'As shown in Figure (a), there is a nested column type *Nested* and two tables *tbl* and *ids*. ' +
      'Nested column type means each row store a structure consists of multiple different value.' +
      'The query shown in Figure (b) joins these two tables on the column *id* using *LEFT ANTI JOIN*. ' +
      '</br></br>' +
      '![Case 0](figures/issue1_query.png =*x100)\n ',
      'Select the most proper description to this case:',
      [
        {id: 0, text: 'A. No optimization issue detected.'},
        {id: 1, text: 'B. Consists of **transformation issue**. A wrong operator *Filter* is added after the *Optimization phase*.'},
        {id: 2, text: 'C. Consists of **transformation issue**. A wrong expression on the operator *Project* is generated after the *Optimization phase*.'},
        {id: 3, text: 'D. Consists of **workflow issue**. A part of optimization steps repeats multiple times but do not change the plan during the *Optimization phase*.'},
      ],
      3
  ),
  new Question(
      'bug4-1',   // N2
      1,
      'As shown in Figure (a), the query uses inner join to join two table *t* and *s* on the column *t\\_col* and *s\\_col*. ' +
      'As the table *t* is a small table, a hint */\\*+ BROADCAST(t) \\*/* is given. ' +
      'The table *t* will be broadcased while executing. ' +
      '</br></br>' +
      '![Case 5](figures/norm2_query.png =*x100)\n' +
      '</br></br>' +
      'Tips: In normal cases, *Broadcaset hint* will be processed as follows: ' +
      '</br>As a single node *ResolvedHint* in the plan in *Analysis phase*;' +
      '</br>Be set to join node in *Optimization phase*;' +
      '</br>Convert to a *BroadcastExchange* node in *Planning phase*.',
      'Select the most proper description to this case:',
      [
        {id: 0, text: 'A. No optimization issue detected.'},
        {id: 1, text: 'B. Consists of **transformation issue**. The *broadcast hint* is missing in the analyzed plan and the executor broadcasts another table *s*.'},
        {id: 2, text: 'C. Consists of **transformation issue**. A wrong optimized plan is generated, which is not equivalent to the original query.'},
        {id: 3, text: 'D. Consists of **workflow issue**. The *hint* does not set to the *InnerJoin* node at the start of optimization.'},
      ],
      0
  ),

  new Question(
      'bug4-0',   // I1
      2,
      'As shown in Figure (a), the query filters the data in the table *t* using *EXISTS* clause, only remaining rows that exist in another table *s*. ' +
      'As the table *t* is a small table, a hint */\\*+ BROADCAST(t) \\*/* is given. ' +
      'The optmizer rewrites the query using *LEFT SEMI JOIN* (as shown in Figure (b)) and the table *t* will be broadcased while executing. ' +
      '</br></br>' +
      '![Case 1](figures/issue3_query.png =*x100)' +
      '</br></br>' +
      'This case consists of a **transformation issue**. The *broadcast hint* is missing and the executor broadcasts another table *s*. This can be found with the position of the *BroadcastExchange* node of physical plan.' +
      '</br></br>' +
      'Tips: In normal cases, *Broadcaset hint* will be processed as follows: ' +
      '</br>As a single node *ResolvedHint* in the plan in *Analysis phase*;' +
      '</br>Be set to join node in *Optimization phase*;' +
      '</br>Convert to a *BroadcastExchange* node in *Planning phase*.',
      'The root cause is that:',
      [
        {id: 0, text: 'A. *RewriteSubquery* step in the *Optimization phase* does not rewrite the *EXISTS* clause properly, so the broadcast hint is removed unexpectedly.'},
        {id: 1, text: 'B. *JoinSelection* step in the *Planning phase* does not convert the broadcast hint properly to the build side choice in *BroadcastHashJoin* node.'},
        {id: 2, text: 'C. *EnsureRequirements* step in the *Planning phase* does not ensure the *BuildLeft* requirement in *BroadcastHashJoin* node.'},
        {id: 3, text: 'D. *ResolveJoinStrategyHints* step in the *Analysis phase* removes the hint node unexpectedly, so the executor chooses to broadcast table *s*.'},
      ],
      3
  ),
  new Question(
      'bug1-0',   // I2
      2,
      'As shown in Figure (a), there is a data source *ids* with three distinct values. ' +
      'The query shown in the below of Figure (a) first derives *ids2* from *ids*, then joins them using *LEFT ANTI JOIN*. ' +
      'The expected join logic is shown in Figure (b). ' +
      '</br></br>' +
      '![Case 2](figures/issue2_query.png =*x180)\n' +
      '</br></br>' +
      'This case consists of **transformation issue**. The optimizer generates a wrong plan that is not equivalent to the original query after the *Optimization phase*.' +
      '</br>' +
      'For the sample data, the correct result would be [4] as 2 and 3 are in *ids*. However, the optimized plan will return [2, 3, 4].' +
      '</br></br>' +
      '**Tips**: Try to track the **join condition** forwards or backwords.',
      'The root cause is that **in Optimization phase**:',
      [
        {id: 0, text: 'A. The join condition is rewritten incorrectly by *PushDownPredicates* step, then the optimizer propagates it and results in an empty selection.'},
        {id: 1, text: 'B. The join condition is rewritten incorrectly by *InferFiltersFromConstraints* step, then the optimizer propagates it and results in an empty selection.'},
        {id: 2, text: 'C. The join condition is rewritten incorrectly by *PushdownLeftSemiAntiJoin* step, then the optimizer propagates it and results in an empty selection.'},
        {id: 3, text: 'D. The join node and the right sub-tree is removed by *PropagateEmptyRelation* step as the right relation is empty, resulting that the plan becomes non-equivalent.'},
      ],
      2
  ),
  new Question(
      'bug0-0',   // I0
      2,
      'As shown in Figure (a), there is a nested column type *Nested* and two tables *tbl* and *ids*. ' +
      'The query shown in Figure (b) joins these two tables on the column *id* using *LEFT ANTI JOIN*. ' +
      '</br></br>' +
      '![Case 0](figures/issue1_query.png =*x100)' +
      '</br></br>' +
      'This case consists of a **workflow issue**. A part of optimization steps repeats multiple times (100 times) and reaches the max iteration threshold.' +
      'However, the plan does not change. ' +
      'This is an optimization loop and most of the steps are useless. ',
      'The root cause is that **in Optimization phase**:',
      [
        {id: 0, text: 'A. *InferFilterFromConstraints* step inserts a useless filter so that the optimizer starts to optimize it multiple times.'},
        {id: 1, text: 'B. *ColumnPruning* step generates two *Project* which are removed later by *RemoveNoopOperators* and *CollapseProject*, so they cancel each other out and form a loop.'},
        {id: 2, text: 'C. *PushDownLeftSemiAntiJoin* step does not push down the *leftAntiJoin* operator successfully so that the optimizer try to optimize it again.'},
        {id: 3, text: 'D. *RemoveNoopOperators* step does not remove the *Project* operator successfully so that the optimizer try to optimize it again.'},
      ],
      1
  ),
]
