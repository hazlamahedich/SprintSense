import React, { useEffect, useRef } from 'react';
import * as d3 from 'd3';
import { WorkItem, Dependency } from '../../types';

interface DependencyGraphProps {
  workItems: WorkItem[];
  dependencies: Dependency[];
  onDependencyClick?: (dependency: Dependency) => void;
  onWorkItemClick?: (workItem: WorkItem) => void;
}

export const DependencyGraph: React.FC<DependencyGraphProps> = ({
  workItems,
  dependencies,
  onDependencyClick,
  onWorkItemClick,
}) => {
  const svgRef = useRef<SVGSVGElement>(null);

  useEffect(() => {
    if (!svgRef.current || !workItems.length) return;

    // Clear previous graph
    d3.select(svgRef.current).selectAll('*').remove();

    // Setup dimensions
    const width = 800;
    const height = 600;
    const margin = { top: 20, right: 20, bottom: 20, left: 20 };

    // Create SVG
    const svg = d3.select(svgRef.current)
      .attr('width', width)
      .attr('height', height);

    // Create simulation
    const simulation = d3.forceSimulation(workItems)
      .force('link', d3.forceLink(dependencies)
        .id(d => (d as WorkItem).id)
        .distance(100))
      .force('charge', d3.forceManyBody().strength(-300))
      .force('center', d3.forceCenter(width / 2, height / 2));

    // Create links
    const links = svg.append('g')
      .selectAll('line')
      .data(dependencies)
      .enter()
      .append('line')
      .attr('stroke', '#999')
      .attr('stroke-opacity', 0.6)
      .attr('stroke-width', d => d.isCritical ? 3 : 1);

    // Create nodes
    const nodes = svg.append('g')
      .selectAll('circle')
      .data(workItems)
      .enter()
      .append('circle')
      .attr('r', 10)
      .attr('fill', d => getNodeColor(d))
      .call(drag(simulation));

    // Add labels
    const labels = svg.append('g')
      .selectAll('text')
      .data(workItems)
      .enter()
      .append('text')
      .text(d => d.title)
      .attr('font-size', '12px')
      .attr('dx', 15)
      .attr('dy', 5);

    // Add tooltips
    const tooltip = d3.select('body').append('div')
      .attr('class', 'dependency-tooltip')
      .style('opacity', 0);

    // Update simulation
    simulation.on('tick', () => {
      links
        .attr('x1', d => (d.source as any).x)
        .attr('y1', d => (d.source as any).y)
        .attr('x2', d => (d.target as any).x)
        .attr('y2', d => (d.target as any).y);

      nodes
        .attr('cx', d => (d as any).x)
        .attr('cy', d => (d as any).y);

      labels
        .attr('x', d => (d as any).x)
        .attr('y', d => (d as any).y);
    });

    // Add interactivity
    nodes.on('mouseover', (event, d) => {
      tooltip.transition()
        .duration(200)
        .style('opacity', .9);
      tooltip.html(getTooltipContent(d))
        .style('left', (event.pageX + 10) + 'px')
        .style('top', (event.pageY - 28) + 'px');
    })
    .on('mouseout', () => {
      tooltip.transition()
        .duration(500)
        .style('opacity', 0);
    })
    .on('click', (event, d) => {
      event.preventDefault();
      event.stopPropagation();
      if (onWorkItemClick && d) onWorkItemClick(d);
    });

    links.on('click', (event, d) => {
      if (onDependencyClick) onDependencyClick(d);
    });

    return () => {
      simulation.stop();
    };
  }, [workItems, dependencies, onDependencyClick, onWorkItemClick]);

  return (
    <div className="dependency-graph">
      <svg ref={svgRef} />
    </div>
  );
};

// Helper functions
const drag = (simulation: d3.Simulation<any, undefined>) => {
  function dragstarted(event: any) {
    if (!event.active) simulation.alphaTarget(0.3).restart();
    event.subject.fx = event.subject.x;
    event.subject.fy = event.subject.y;
  }

  function dragged(event: any) {
    event.subject.fx = event.x;
    event.subject.fy = event.y;
  }

  function dragended(event: any) {
    if (!event.active) simulation.alphaTarget(0);
    event.subject.fx = null;
    event.subject.fy = null;
  }

  return d3.drag()
    .on('start', dragstarted)
    .on('drag', dragged)
    .on('end', dragended);
};

const getNodeColor = (workItem: WorkItem): string => {
  switch (workItem.status) {
    case 'completed':
      return '#4CAF50';
    case 'in_progress':
      return '#2196F3';
    case 'blocked':
      return '#F44336';
    default:
      return '#9E9E9E';
  }
};

const getTooltipContent = (workItem: WorkItem): string => {
  return `
    <div class="tooltip-content">
      <h4>${workItem.title}</h4>
      <p>Status: ${workItem.status}</p>
      <p>Priority: ${workItem.priority}</p>
      ${workItem.dependencies?.length ?
        `<p>Dependencies: ${workItem.dependencies.length}</p>` : ''}
    </div>
  `;
};
