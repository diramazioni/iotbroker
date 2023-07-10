"use client";

import {
    Card,
    Grid,
    Title,
    Text,
    Tab,
    TabList,
    TabGroup,
    TabPanel,
    TabPanels,
} from "@tremor/react";
 
import KpiCardGrid from "../components/cards"
import ChartView from "../components/chart"
import TrackerCard from "../components/track"
import SalesPeopleTable from "../components/table"

export default function Dashboard() {
    return (
        <main className="px-12 py-12">
            <Title>Dashboard</Title>
            <Text>IoT dashboard for the sensors </Text>

            <TabGroup className="mt-6">
                <TabList>
                    <Tab>Overview</Tab>
                    <Tab>Detail</Tab>
                </TabList>
                <TabPanels>
                    <TabPanel>
                        <KpiCardGrid/>
                        <div className="mt-6">
                            <TrackerCard />
                        </div>
                        <div className="mt-6">
                            <ChartView/>
                        </div>
                    </TabPanel>
                    <TabPanel>
                        <div className="mt-6">
                            <SalesPeopleTable/>
                        </div>
                    </TabPanel>
                </TabPanels>
            </TabGroup>
        </main>
    );
}
