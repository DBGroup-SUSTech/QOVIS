export const Patterns = [
  {
    name: "Root",
    type: "Root",
    items: [
      {
        name: "Analysis",
        desc: "?"
      },
      {
        name: "Optimization",
        desc: "?"
      },
      {
        name: "Planning",
        desc: "?"
      },
      {
        name: "AQE",
        desc: "*"
      }
    ]
  },
  {
    name: "Analysis",
    type: "Phase",
    items: [
      {
        name: "Resolution",
        desc: "?"
      },
      {
        name: "Finish Analysis",
        desc: "?"
      }
    ]
  },
  {
    name: "Resolution",
    type: "Batch",
    items: [
      {
        name: "ResolveRelations",
        desc: "*"
      },
      {
        name: "SoftTrans",
        desc: "?",
      },
      {
        name: "DeduplicateRelations",
        desc: "*",
      },
      {
        name: "ResolveReferences",
        desc: "?"
      },
      {
        name: "ResolveFunctions",
        desc: "?"
      },
      {
        name: "GlobalAggregates",
        desc: "?"
      }
    ]
  },
  {
    name: "ResolveRelations",
    type: "Action"
  },
  {
    name: "ResolveReferences",
    type: "Action"
  },
  {
    name: "ResolveFunctions",
    type: "Action"
  },
  {
    name: "GlobalAggregates",
    type: "Action"
  },
  {
    name: "Finish Analysis",
    type: "Batch",
    items: [
      {
        name: "FinishAnalysis",
        desc: "?"
      }
    ]
  },
  {
    name: "FinishAnalysis",
    type: "Action"
  },
  // optimization
  {
    name: "Optimization",
    type: "Phase",
    items: [
      {
        name: "Union",
        desc: "?"
      },
      {
        name: "Operator Optimization before Inferring Filters",
        desc: "*"
      },
      {
        name: "Infer Filters",
        desc: "?"
      },
      {
        name: "Operator Optimization after Inferring Filters",
        desc: "*"
      }
    ]
  },
  {
    name: "Union",
    type: "Batch",
    items: [
      {
        name: "RemoveNoopOperators",
        desc: "?"
      },
      {
        name: "CombineUnions",
        desc: "?"
      },
      {
        name: "RemoveNoopUnion",
        desc: "?"
      }
    ]
  },
  {
    name: "RemoveNoopOperators",
    type: "Action"
  },
  {
    name: "CombineUnions",
    type: "Action"
  },
  {
    name: "RemoveNoopUnion",
    type: "Action"
  },
  {
    name: "Operator Optimization before Inferring Filters",
    type: "Batch",
    items: [
      {
        name: "PushDownPredicates",
        desc: "?"
      },
      {
        name: "PushDownLeftSemiAntiJoin",
        desc: "?"
      },
      {
        name: "ColumnPruning",
        desc: "?"
      },
      {
        name: "CollapseProject",
        desc: "?"
      },
      {
        name: "RemoveNoopOperators",
        desc: "?"
      }
    ]
  },
  {
    name: "PushDownLeftSemiAntiJoin",
    type: "Action"
  },
  {
    name: "ColumnPruning",
    type: "Action"
  },
  {
    name: "CollapseProject",
    type: "Action"
  },
  {
    name: "RemoveNoopOperators",
    type: "Action"
  },
  {
    name: "Infer Filters",
    type: "Batch",
    items: [
      {
        name: "InferFiltersFromConstraints",
        desc: "?"
      }
    ]
  },
  {
    name: "InferFiltersFromConstraints",
    type: "Action"
  },
  {
    name: "Operator Optimization after Inferring Filters",
    type: "Batch",
    items: [
      {
        name: "PushDownLeftSemiAntiJoin",
        desc: "?"
      },
      {
        name: "ColumnPruning",
        desc: "?"
      },
      {
        name: "CollapseProject",
        desc: "?"
      },
      {
        name: "RemoveNoopOperators",
        desc: "?"
      }
    ]
  },
  {
    name: "Planning",
    type: "Phase",
    items: [
      {
        name: "Prepare Planning",
        desc: "?"
      },
      {
        name: "Physical Planning",
        desc: "?"
      },
//      {
//        name: "Prepare Execution",
//        desc: "?"
//      }
    ]
  },
  {
    name: "Prepare Planning",
    type: "Batch",
    items: [
      {
        name: "InsertReturnAnswer",
        desc: "?"
      }
    ]
  },
  {
    name: "InsertReturnAnswer",
    type: "Action"
  },
  {
    name: "Physical Planning",
    type: "Batch",
    items: [
      {
        name: "SpecialLimits",
        desc: "?"
      },
      {
        name: "Aggregation",
        desc: "?"
      },
      {
        name: "JoinSelection",
        desc: "?"
      },
      // {
      //   name: "LogicalQueryStageStrategy",
      //   desc: "*",
      // },
      {
        name: "InMemoryScans",
        desc: "*"
      },
      {
        name: "BasicOperators",
        desc: "*"
      },
      // {
      //   name: "SoftTrans",
      //   desc: "*"
      // },
      {
        name: "EnsureRequirements",
        desc: "*",
      },
      {
        name: "CreateQueryStages",
        desc: "?",
      }
    ]
  },
  {
    name: "SpecialLimits",
    type: "Action"
  },
  {
    name: "Aggregation",
    type: "Action"
  },
  {
    name: "JoinSelection",
    type: "Action"
  },
  {
    name: "InMemoryScans",
    type: "Action"
  },
  {
    name: "BasicOperators",
    type: "Action"
  },
  {
    name: "EnsureRequirements",
    type: "Action"
  },
  {
    name: "Prepare Execution",
    type: "Batch",
    items: [
      {
        name: "EnsureRequirements",
        desc: "*"
      }
    ]
  },
  {
    name: "AQE",
    type: "Phase",
    items: [
      {
        name: "AQE Process Logical Query Stage",
        desc: "*"
      },
      {
        name: "Propagate Empty Relations",
        desc: "?"
      },
      {
        name: "Dynamic Join Selection",
        desc: "?"
      },
      {
        name: "AQE Replanning Preparation",
        desc: "?"
      },
      {
        name: "Physical Planning",
        desc: "?"
      },
      {
        name: "AQE Query Stage Optimization",
        desc: "?"
      },
      {
        name: "AQE Post Stage Creation",
        desc: "*"
      },
      {
        name: "Create Query Stages",
        desc: "?"
      }
    ]
  },
  {
    name: "AQE Process Logical Query Stage",
    type: "Batch",
    items: [
      {
        name: "ReplaceWithLogicalQueryStage",
        desc: "?"
      }
    ]
  },
  {
    name: "ReplaceWithLogicalQueryStage",
    type: "Action"
  },
  {
    name: "Propagate Empty Relations",
    type: "Batch",
    items: [
      {
        name: "AQEPropagateEmptyRelation",
        desc: "?"
      }
    ]
  },
  {
    name: "AQEPropagateEmptyRelation",
    type: "Action"
  },
  {
    name: "Dynamic Join Selection",
    type: "Batch",
    items: [
      {
        name: "DynamicJoinSelection",
        desc: "?"
      }
    ]
  },
  {
    name: "DynamicJoinSelection",
    type: "Action"
  },
  {
    name: "AQE Replanning Preparation",
    type: "Batch",
    items: [
      {
        name: "InsertReturnAnswer",
        desc: "?"
      }
    ]
  },
  {
    name: "AQE Query Stage Optimization",
    type: "Batch",
    items: [
      {
        name: "CoalesceShufflePartitions",
        desc: "?"
      },
      {
        name: "OptimizeShuffleWithLocalRead",
        desc: "?"
      }
    ]
  },
  {
    name: "CoalesceShufflePartitions",
    type: "Action"
  },
  {
    name: "OptimizeShuffleWithLocalRead",
    type: "Action"
  },
  {
    name: "AQE Post Stage Creation",
    type: "Batch",
    items: [
      {
        name: "CollapseCodegenStages",
        desc: "?"
      }
    ]
  },
  {
    name: "CollapseCodegenStages",
    type: "Action"
  },
  {
    name: "Create Query Stages",
    type: "Batch",
    items: [
      {
        name: "CreateQueryStages",
        desc: "?"
      }
    ]
  },
  {
    name: "CreateQueryStages",
    type: "Action"
  },
]
