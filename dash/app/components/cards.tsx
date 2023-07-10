"use client";

import { BadgeDelta, Card, Grid, DeltaType, Flex, Metric, CategoryBar, Text } from "@tremor/react";

type Kpi = {
    title: string;
    metric: string;
    progress: number;
    target: string;
    delta: string;
    deltaType: DeltaType;
};

const kpiData: Kpi[] = [
    {
        title: "Average Temperatures",
        metric: "15 C",
        progress: 15.9,
        target: "July",
        delta: "13.2%",
        deltaType: "moderateIncrease",
    },
    {
        title: "Average Humidity 7am-7pm",
        metric: "60%",
        progress: 60,
        target: "July",
        delta: "23.9%",
        deltaType: "moderateDecrease",
    },
    {
        title: "Average UV index",
        metric: "7,072",
        progress: 70,
        target: "July",
        delta: "10.1%",
        deltaType: "moderateIncrease",
    },
];

export default function KpiCardGrid() {
    return (
        <Grid numItemsLg={3} className="mt-6 gap-6">
            {kpiData.map((item) => (
                <Card key={item.title}>
                    <Flex alignItems="start">
                        <div className="truncate">
                            <Text>{item.title}</Text>
                            <Metric className="truncate">{item.metric}</Metric>
                        </div>
                        <BadgeDelta deltaType={item.deltaType}>{item.delta}</BadgeDelta>
                    </Flex>
                    <Flex className="mt-4 space-x-2">
                        <Text className="truncate">{`${item.progress}% (${item.metric})`}</Text>
                        <Text>{item.target}</Text>
                    </Flex>
                    <CategoryBar values={[40, 30, 20, 10]} colors={["emerald", "yellow", "orange", "rose"]} markerValue={item.progress} showLabels={false} className="mt-2" />
                </Card>
            ))}
        </Grid>
    );
}
