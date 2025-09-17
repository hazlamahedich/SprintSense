import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import axios from 'axios'
import { workItemService } from '../workItemService'
import {
  WorkItemType,
  WorkItemStatus,
  SortOrder,
} from '../../types/workItem.types'

vi.mock('axios')

const mockedAxios = vi.mocked(axios, true)

describe('workItemService', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  afterEach(() => {
    vi.resetAllMocks()
  })

  describe('getWorkItems', () => {
    it('should fetch work items with basic parameters', async () => {
      const mockResponse = {
        data: {
          items: [
            {
              id: '1',
              team_id: 'team-1',
              author_id: 'user-author',
              title: 'Test Item',
              type: WorkItemType.TASK,
              status: WorkItemStatus.BACKLOG,
              priority: 3.0,
              created_at: '2023-01-01T00:00:00.000Z',
              updated_at: '2023-01-01T00:00:00.000Z',
            },
          ],
          total: 1,
          page: 1,
          size: 20,
        },
      }

      mockedAxios.get.mockResolvedValue(mockResponse)

      const result = await workItemService.getWorkItems('team-1')

      expect(mockedAxios.get).toHaveBeenCalledWith(
        '/api/v1/teams/team-1/work-items',
        {
          params: {
            page: 1,
            size: 20,
          },
        }
      )

      expect(result).toEqual(mockResponse.data)
    })

    it('should fetch work items with filters', async () => {
      const mockResponse = {
        data: {
          items: [],
          total: 0,
          page: 1,
          size: 20,
        },
      }

      mockedAxios.get.mockResolvedValue(mockResponse)

      const filters = {
        search: 'test',
        types: [WorkItemType.BUG],
        statuses: [WorkItemStatus.BACKLOG, WorkItemStatus.TODO],
        assigneeId: 'user-1',
      }

      const sort = {
        field: 'priority',
        order: SortOrder.DESC,
      }

      await workItemService.getWorkItems('team-1', {
        filters,
        sort,
        page: 2,
        size: 10,
      })

      expect(mockedAxios.get).toHaveBeenCalledWith(
        '/api/v1/teams/team-1/work-items',
        {
          params: {
            page: 2,
            size: 10,
            search: 'test',
            types: 'bug',
            statuses: 'backlog,todo',
            assigneeId: 'user-1',
            sortField: 'priority',
            sortOrder: 'desc',
          },
        }
      )
    })

    it('should handle API errors', async () => {
      const error = new Error('Network Error')
      mockedAxios.get.mockRejectedValue(error)

      await expect(workItemService.getWorkItems('team-1')).rejects.toThrow(
        'Network Error'
      )
    })
  })

  describe('createWorkItem', () => {
    it('should create a work item', async () => {
      const newWorkItem = {
        title: 'New Task',
        description: 'A new task description',
        type: WorkItemType.TASK,
        status: WorkItemStatus.BACKLOG,
        priority: 3.0,
        storyPoints: 3,
      }

      const mockResponse = {
        data: {
          id: '123',
          team_id: 'team-1',
          author_id: 'user-author',
          ...newWorkItem,
          created_at: '2023-01-01T00:00:00.000Z',
          updated_at: '2023-01-01T00:00:00.000Z',
        },
      }

      mockedAxios.post.mockResolvedValue(mockResponse)

      const result = await workItemService.createWorkItem('team-1', newWorkItem)

      expect(mockedAxios.post).toHaveBeenCalledWith(
        '/api/v1/teams/team-1/work-items',
        newWorkItem
      )

      expect(result).toEqual(mockResponse.data)
    })

    it('should handle creation errors', async () => {
      const newWorkItem = {
        title: 'New Task',
        type: WorkItemType.TASK,
        status: WorkItemStatus.BACKLOG,
        priority: 3.0,
      }

      const error = {
        response: {
          status: 400,
          data: { message: 'Invalid data' },
        },
      }

      mockedAxios.post.mockRejectedValue(error)

      await expect(
        workItemService.createWorkItem('team-1', newWorkItem)
      ).rejects.toEqual(error)
    })
  })

  describe('updateWorkItem', () => {
    it('should update a work item', async () => {
      const updates = {
        title: 'Updated Title',
        status: WorkItemStatus.DONE,
        priority: 1.0,
      }

      const mockResponse = {
        data: {
          id: '123',
          team_id: 'team-1',
          author_id: 'user-author',
          ...updates,
          type: WorkItemType.TASK,
          created_at: '2023-01-01T00:00:00.000Z',
          updated_at: '2023-01-02T00:00:00.000Z',
        },
      }

      mockedAxios.patch.mockResolvedValue(mockResponse)

      const result = await workItemService.updateWorkItem(
        'team-1',
        '123',
        updates
      )

      expect(mockedAxios.patch).toHaveBeenCalledWith(
        '/api/v1/teams/team-1/work-items/123',
        updates
      )

      expect(result).toEqual(mockResponse.data)
    })
  })

  describe('deleteWorkItem', () => {
    it('should delete a work item', async () => {
      mockedAxios.delete.mockResolvedValue({ data: {} })

      await workItemService.deleteWorkItem('team-1', '123')

      expect(mockedAxios.delete).toHaveBeenCalledWith(
        '/api/v1/teams/team-1/work-items/123'
      )
    })

    it('should handle delete errors', async () => {
      const error = {
        response: {
          status: 404,
          data: { message: 'Work item not found' },
        },
      }

      mockedAxios.delete.mockRejectedValue(error)

      await expect(
        workItemService.deleteWorkItem('team-1', '123')
      ).rejects.toEqual(error)
    })
  })

  describe('getWorkItem', () => {
    it('should fetch a single work item', async () => {
      const mockResponse = {
        data: {
          id: '123',
          team_id: 'team-1',
          author_id: 'user-author',
          title: 'Test Item',
          type: WorkItemType.TASK,
          status: WorkItemStatus.BACKLOG,
          priority: 3.0,
          created_at: '2023-01-01T00:00:00.000Z',
          updated_at: '2023-01-01T00:00:00.000Z',
        },
      }

      mockedAxios.get.mockResolvedValue(mockResponse)

      const result = await workItemService.getWorkItem('team-1', '123')

      expect(mockedAxios.get).toHaveBeenCalledWith(
        '/api/v1/teams/team-1/work-items/123'
      )
      expect(result).toEqual(mockResponse.data)
    })
  })
})
